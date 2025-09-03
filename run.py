import os

from dotenv import load_dotenv

from app import create_app
from app.services.rbac_init_service import RBACInitService

load_dotenv()

config_name = os.getenv('FLASK_ENV', 'development')
app = create_app(config_name)

if __name__ == '__main__':
    # with app.app_context():
    #     RBACInitService.init_all()

    # 启动应用
    app.run(
        host='0.0.0.0',
        port=int(os.getenv('PORT', 5000)),
        debug=app.config.get('DEBUG', False),
        threaded=app.config.get('THREADED', True)
    )
