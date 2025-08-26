from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '10eb1a908c44'
down_revision = 'e1e5f8eaf753'
branch_labels = None
depends_on = None

def upgrade():
    op.create_table(
        'medical_equipment_ledger',
        
        sa.Column('ledger_id', sa.Integer,
            primary_key=True, 
            autoincrement=True, 
            nullable=False, 
            
        ),
        
        sa.Column('medical_id', sa.Integer,
            
            
            nullable=False, 
            
        ),
        
        sa.Column('model_number', sa.Text,
            
            
            nullable=False, 
            
        ),
        
        sa.Column('product_name', sa.Text,
            
            
            
            
        ),
        
        sa.Column('maker_name', sa.Text,
            
            
            
            
        ),
        
        sa.Column('classification_id', sa.Integer,
            
            
            
            
        ),
        
        sa.Column('stock_quantity', sa.Integer,
            
            
            nullable=False, 
            
        ),
        
        sa.Column('is_included', sa.Boolean,
            
            
            nullable=False, 
            
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
    op.drop_table('medical_equipment_ledger')