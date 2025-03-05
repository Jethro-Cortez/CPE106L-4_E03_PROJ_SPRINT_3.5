"""Add genre, publication_year, and isbn to books

Revision ID: a1171e3f7f1f
Revises: b85f94178614
Create Date: 2025-03-01 20:55:09.236032

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a1171e3f7f1f'
down_revision = 'b85f94178614'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('books', schema=None) as batch_op:
        batch_op.add_column(sa.Column('genre', sa.String(length=100), nullable=True))
        batch_op.add_column(sa.Column('publication_year', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('isbn', sa.String(length=20), nullable=True))


def downgrade():
    with op.batch_alter_table('books', schema=None) as batch_op:
        batch_op.add_column(sa.Column('category', sa.VARCHAR(length=100), nullable=True))

