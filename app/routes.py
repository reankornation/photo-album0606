import os
from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app, abort
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from app.models import db, User, Album, Photo
from app.utils import upload_to_s3



bp = Blueprint('app', __name__)

@bp.route('/')
def home():
    return render_template('home.html')

@bp.route('/login', methods=['GET', 'POST'])
def login():
    from app.forms import LoginForm
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and check_password_hash(user.password, form.password.data):
            login_user(user)
            flash('Ви успішно увійшли!', 'success')
            return redirect(url_for('app.album'))
        else:
            flash('Невірний email або пароль. Спробуйте ще раз.', 'danger')
    return render_template('login.html', form=form)

@bp.route('/register', methods=['GET', 'POST'])
def register():
    from app.forms import RegistrationForm
    form = RegistrationForm()
    if form.validate_on_submit():
        existing_user = User.query.filter_by(email=form.email.data).first()
        if existing_user:
            flash('Цей email вже зареєстровано. Спробуйте інший.', 'danger')
            return render_template('register.html', form=form)
        hashed_password = generate_password_hash(form.password.data, method='pbkdf2:sha256')
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash('Ваш акаунт створено! Тепер ви можете увійти.', 'success')
        return redirect(url_for('app.login'))
    return render_template('register.html', form=form)

@bp.route('/album', methods=['GET', 'POST'])
@login_required
def album():
    if request.method == 'POST':
        folder_name = request.form.get('folder_name')
        if folder_name:
            new_album = Album(name=folder_name, owner=current_user, parent_id=None)
            db.session.add(new_album)
            db.session.commit()
            flash('Папку створено успішно!', 'success')
    top_albums = Album.query.filter_by(user_id=current_user.id, parent_id=None).all()
    return render_template('album.html', albums=top_albums)

@bp.route('/album/<int:album_id>', methods=['GET', 'POST'])
@login_required
def view_album(album_id):
    album = Album.query.get_or_404(album_id)
    if request.method == 'POST':
        folder_name = request.form.get('folder_name')
        photo = request.files.get('photo')
        
        if folder_name:  
            new_album = Album(name=folder_name, owner=current_user, parent_id=album.id)
            db.session.add(new_album)
            db.session.commit()
            flash('Підпапку створено успішно!', 'success')
        elif photo: 
            filename = secure_filename(photo.filename)
            if not filename:
                flash("Невірний формат файлу!", "danger")
                return redirect(url_for('app.view_album', album_id=album.id))
            
            try:
                
                file_url = upload_to_s3(photo, filename)  
                if file_url:
                   
                    new_photo = Photo(file_path=file_url, album=album)
                    db.session.add(new_photo)
                    db.session.commit()
                    flash('Фото завантажено на S3 успішно!', 'success')
                else:
                    flash('Помилка завантаження фото на S3!', 'danger')
            except Exception as e:
                flash(f"Помилка завантаження: {e}", 'danger')
                return redirect(url_for('app.view_album', album_id=album.id))

    
    subalbums = Album.query.filter_by(parent_id=album.id).all()
    photos = Photo.query.filter_by(album_id=album.id).all()
    return render_template('view_album.html', album=album, subalbums=subalbums, photos=photos)


@bp.route('/album/delete/<int:album_id>', methods=['POST'])
@login_required
def delete_album(album_id):
    album = Album.query.get_or_404(album_id)
    if album.owner is not None and album.owner != current_user:
        abort(403)
    db.session.delete(album)
    db.session.commit()
    flash('Папку видалено!', 'success')
    return redirect(request.referrer or url_for('app.album'))

@bp.route('/shared_album', methods=['GET', 'POST'])
@login_required
def shared_album():
    parent_id = request.args.get('parent_id', None)  
    folder_name = request.form.get('folder_name')  
    photo = request.files.get('photo')  

    print(f"POST запит: folder_name={folder_name}, photo={photo}")

    if request.method == 'POST':
        if folder_name:  
            print(f"Створення нової папки: {folder_name}")
            new_album = Album(name=folder_name, user_id=None, parent_id=parent_id) 
            db.session.add(new_album)
            db.session.commit()
            flash('Папка створена!', 'success')
        elif photo: 
            print(f"Отримано файл: {photo.filename}")
            filename = secure_filename(photo.filename)
            if not filename:
                flash("Невірний формат файлу!", "danger")
                return redirect(url_for('app.shared_album', parent_id=parent_id))

            try:
                
                file_url = upload_to_s3(photo, filename)
                if file_url:
                    print(f"Фото завантажено на S3. URL: {file_url}")
                   
                    new_photo = Photo(file_path=file_url, album_id=parent_id, shared=True)
                    db.session.add(new_photo)
                    db.session.commit()
                    flash('Фото успішно завантажено на S3!', 'success')
                else:
                    print("Помилка під час завантаження на S3.")
                    flash('Помилка завантаження фото на S3!', 'danger')
            except Exception as e:
                print(f"Помилка завантаження файлу: {e}")
                flash(f"Помилка завантаження файлу: {e}", "danger")
                return redirect(url_for('app.shared_album', parent_id=parent_id))


    current_folder = None
    if parent_id:
        current_folder = Album.query.get_or_404(parent_id)

    subalbums = Album.query.filter_by(parent_id=parent_id, user_id=None).all() 
    photos = Photo.query.filter_by(album_id=parent_id).all()

    return render_template(
        'shared_album.html',
        current_folder=current_folder,
        subalbums=subalbums,
        photos=photos,
    )



@bp.route('/photo/delete/<int:photo_id>', methods=['POST'])
@login_required
def delete_photo(photo_id):
    photo = Photo.query.get_or_404(photo_id)

    file_path = os.path.join(current_app.static_folder, photo.file_path)
    if os.path.exists(file_path):
        os.remove(file_path)

    db.session.delete(photo)
    db.session.commit()

    flash('Фото видалено успішно!', 'success')
    return redirect(request.referrer or url_for('app.shared_album'))





@bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('app.home'))
