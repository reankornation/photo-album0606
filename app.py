from app import create_app
from app.routes import bp as app_bp 
from app.utils import upload_to_s3 


app = create_app()


app.register_blueprint(app_bp)


@app.route('/test_upload', methods=['GET'])
def test_upload():
    try:
        with open('test.jpg', 'rb') as file:
            url = upload_to_s3(file, 'test.jpg') 
            if url:
                return f"Фото успішно завантажено на S3. URL: {url}"
            else:
                return "Фото не завантажено."
    except Exception as e:
        return f"Помилка: {e}"

if __name__ == '__main__':
    app.run(debug=True)
