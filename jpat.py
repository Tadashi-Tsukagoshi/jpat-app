import os
from flask import Flask, request, redirect, render_template, flash
from werkzeug.utils import secure_filename
from tensorflow.keras.models import Sequential, load_model
from tensorflow.keras.preprocessing import image
from tensorflow.keras.optimizers import SGD  # SGDをインポートする

import numpy as np

classes = ["「 青海波 SEIGAIHA 」","「 七宝  SHIPPOU 」","「 紗綾形  SAYAGATA 」","「 矢絣  YAGASURI 」","「 三崩し  SANKUZUSHI 」","「 縞  SHIMA 」"]
image_size = 100

UPLOAD_FOLDER = "uploads"
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])

app = Flask(__name__)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

###model = load_model('./model.h5') #学習済みモデルをロード

# SGDオプティマイザを再定義
class CustomSGD(SGD):
    pass

# モデルをロードする際にカスタムオブジェクトとして指定
model = load_model('./model.h5', custom_objects={'CustomSGD': CustomSGD})


@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('ファイルがありません')
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            flash('ファイルがありません')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(UPLOAD_FOLDER, filename))
            filepath = os.path.join(UPLOAD_FOLDER, filename)

            #受け取った画像を読み込み、np形式に変換
            img = image.load_img(filepath, grayscale=False, target_size=(image_size,image_size)) ##True→Falseへ変更
            img = image.img_to_array(img)
            data = np.array([img])
            #変換したデータをモデルに渡して予測する
            result = model.predict(data)[0]
            predicted = result.argmax()
            pred_answer = "模様は" + classes[predicted] + "です"

            return render_template("index.html",answer=pred_answer)

    return render_template("index.html",answer="")


##サーバーの設定
##if __name__ == "__main__":
##    app.run()

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 8080))
    app.run(host ='0.0.0.0',port = port)
