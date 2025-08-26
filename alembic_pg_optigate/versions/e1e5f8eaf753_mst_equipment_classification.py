from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'e1e5f8eaf753'
down_revision = '7721cd10c51f'
branch_labels = None
depends_on = None

def upgrade():
    op.create_table(
        'mst_equipment_classification',
        
        sa.Column('classification_id', sa.Integer,
            primary_key=True, 
            autoincrement=True, 
            nullable=False, 
            
        ),
        
        sa.Column('medical_id', sa.Integer,
            
            
            
            
        ),
        
        sa.Column('classification_level', sa.Integer,
            
            
            nullable=False, 
            
        ),
        
        sa.Column('classification_name', sa.Text,
            
            
            nullable=False, 
            
        ),
        
        sa.Column('parent_classification_id', sa.Integer,
            
            
            
            
        ),
        
        sa.Column('publication_classification_id', sa.Integer,
            
            
            
            
        ),
        
        sa.Column('reg_user_id', sa.Text,
            
            
            nullable=False, 
            
        ),
        
        sa.Column('regdate', sa.DateTime,
            
            
            nullable=False, 
            
        ),
        
        sa.Column('update_user_id', sa.Text,
            
            
            nullable=False, 
            
        ),
        
        sa.Column('lastupdate', sa.DateTime,
            
            
            nullable=False, 
            
        ),
        
    )

def downgrade():
    op.drop_table('mst_equipment_classification')