from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '35aec7555393'
down_revision = '4cf14d626491'
branch_labels = None
depends_on = None

def upgrade():
    op.create_table(
        'report_publication_log',
        
        sa.Column('publication_id', sa.Integer,
            primary_key=True, 
            autoincrement=True, 
            nullable=False, 
            
        ),
        
        sa.Column('medical_id', sa.Integer,
            
            
            nullable=False, 
            
        ),
        
        sa.Column('publication_ym', sa.Text,
            
            
            nullable=False, 
            
        ),
        
        sa.Column('file_type', sa.Integer,
            
            
            nullable=False, 
            
        ),
        
        sa.Column('file_name', sa.Text,
            
            
            nullable=False, 
            
        ),
        
        sa.Column('upload_datetime', sa.DateTime,
            
            
            nullable=False, 
            
        ),
        
        sa.Column('download_user_id', sa.Text,
            
            
            nullable=False, 
            
        ),
        
        sa.Column('download_datetime', sa.DateTime,
            
            
            
            
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
    op.drop_table('report_publication_log')