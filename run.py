from app import create_app

# 创建应用实例
app = create_app()

if __name__ == '__main__':
    app.run(debug=True)
