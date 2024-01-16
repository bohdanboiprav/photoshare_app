"""Init

Revision ID: 1adda4154790
Revises: 09868c6cd902
Create Date: 2024-01-15 01:21:32.306186

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '1adda4154790'
down_revision: Union[str, None] = '09868c6cd902'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('tags_to_posts')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('tags_to_posts',
    sa.Column('post_id', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('tag_id', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('id', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.ForeignKeyConstraint(['post_id'], ['posts.id'], name='tags_to_posts_post_id_fkey'),
    sa.ForeignKeyConstraint(['tag_id'], ['tags.id'], name='tags_to_posts_tag_id_fkey')
    )
    # ### end Alembic commands ###