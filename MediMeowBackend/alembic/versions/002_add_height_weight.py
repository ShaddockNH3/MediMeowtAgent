"""Add height and weight to questionnaire_submissions

Revision ID: 002
Revises: 001
Create Date: 2025-01-17

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '002'
down_revision = '001'
branch_labels = None
depends_on = None


def upgrade():
    # 添加 height 和 weight 列到 questionnaire_submissions 表
    op.add_column('questionnaire_submissions', sa.Column('height', sa.Integer(), nullable=True, comment='身高(cm)'))
    op.add_column('questionnaire_submissions', sa.Column('weight', sa.Integer(), nullable=True, comment='体重(kg)'))


def downgrade():
    op.drop_column('questionnaire_submissions', 'weight')
    op.drop_column('questionnaire_submissions', 'height')
