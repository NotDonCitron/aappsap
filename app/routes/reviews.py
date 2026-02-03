"""Product review routes."""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy import func
from app import db
from app.models import Review, Product
from app.routes.auth import admin_required

reviews_bp = Blueprint('reviews', __name__, url_prefix='/api/v1/reviews')


@reviews_bp.route('/product/<int:product_id>', methods=['GET'])
def get_product_reviews(product_id):
    """Get all approved reviews for a product."""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    
    # Check if product exists
    product = Product.query.get_or_404(product_id)
    
    # Get reviews
    reviews = Review.query.filter_by(
        product_id=product_id,
        is_approved=True
    ).order_by(Review.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    # Calculate average rating
    avg_rating = db.session.query(func.avg(Review.rating)).filter_by(
        product_id=product_id,
        is_approved=True
    ).scalar() or 0
    
    # Get rating distribution
    rating_counts = db.session.query(
        Review.rating, func.count(Review.id)
    ).filter_by(
        product_id=product_id,
        is_approved=True
    ).group_by(Review.rating).all()
    
    distribution = {str(i): 0 for i in range(1, 6)}
    for rating, count in rating_counts:
        distribution[str(rating)] = count
    
    return jsonify({
        'reviews': [r.to_dict() for r in reviews.items],
        'pagination': {
            'page': page,
            'per_page': per_page,
            'total': reviews.total,
            'pages': reviews.pages
        },
        'summary': {
            'average_rating': round(float(avg_rating), 1),
            'total_reviews': reviews.total,
            'distribution': distribution
        }
    })


@reviews_bp.route('', methods=['POST'])
@jwt_required()
def create_review():
    """Create a new review."""
    user_id = int(get_jwt_identity())
    data = request.get_json()
    
    product_id = data.get('product_id')
    rating = data.get('rating')
    comment = data.get('comment', '')
    
    if not product_id or not rating:
        return jsonify({'error': 'product_id and rating required'}), 400
    
    if not 1 <= rating <= 5:
        return jsonify({'error': 'Rating must be between 1 and 5'}), 400
    
    # Check if product exists
    product = Product.query.get_or_404(product_id)
    
    # Check if user already reviewed this product
    existing = Review.query.filter_by(
        user_id=user_id,
        product_id=product_id
    ).first()
    
    if existing:
        return jsonify({'error': 'You have already reviewed this product'}), 409
    
    review = Review(
        user_id=user_id,
        product_id=product_id,
        rating=rating,
        comment=comment,
        is_approved=True  # Auto-approve for now
    )
    
    db.session.add(review)
    db.session.commit()
    
    return jsonify({
        'message': 'Review created',
        'review': review.to_dict()
    }), 201


@reviews_bp.route('/<int:review_id>', methods=['DELETE'])
@jwt_required()
def delete_review(review_id):
    """Delete own review or admin can delete any."""
    user_id = int(get_jwt_identity())
    
    review = Review.query.get_or_404(review_id)
    
    # Check if user owns the review or is admin
    from app.models import User
    user = User.query.get(user_id)
    
    if review.user_id != user_id and not user.is_admin():
        return jsonify({'error': 'Not authorized'}), 403
    
    db.session.delete(review)
    db.session.commit()
    
    return jsonify({'message': 'Review deleted'})


@reviews_bp.route('/pending', methods=['GET'])
@admin_required
def get_pending_reviews():
    """Get pending reviews for approval (admin only)."""
    reviews = Review.query.filter_by(is_approved=False).all()
    return jsonify({'reviews': [r.to_dict() for r in reviews]})


@reviews_bp.route('/<int:review_id>/approve', methods=['POST'])
@admin_required
def approve_review(review_id):
    """Approve a review (admin only)."""
    review = Review.query.get_or_404(review_id)
    review.is_approved = True
    db.session.commit()
    
    return jsonify({
        'message': 'Review approved',
        'review': review.to_dict()
    })
