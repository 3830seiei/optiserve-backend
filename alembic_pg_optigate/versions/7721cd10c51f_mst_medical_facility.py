from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '7721cd10c51f'
down_revision = '20ac8a442bb7'
branch_labels = None
depends_on = None

def upgrade():
    op.create_table(
        'mst_medical_facility',
        
        sa.Column('medical_id', sa.Integer,
            primary_key=True, 
            autoincrement=True, 
            nullable=False, 
            
        ),
        
        sa.Column('medical_name', sa.Text,
            
            
            nullable=False, 
            
        ),
        
        sa.Column('address_postal_code', sa.Text,
            
            
            
            
        ),
        
        sa.Column('address_prefecture', sa.Text,
            
            
            
            
        ),
        
        sa.Column('address_city', sa.Text,
            
            
            
            
        ),
        
        sa.Column('address_line1', sa.Text,
            
            
            
            
        ),
        
        sa.Column('address_line2', sa.Text,
            
            
            
            
        ),
        
        sa.Column('phone_number', sa.Text,
            
            
            
            
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
    op.drop_table('mst_medical_facility')