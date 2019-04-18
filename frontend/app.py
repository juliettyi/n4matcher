from flask import Flask, render_template, flash, redirect, request
from flask_wtf import Form
from flask_wtf.file import FileField
from tools import check_result
from tools import s3_upload

app = Flask(__name__)
app.config.from_object('config')

class UploadForm(Form):
  images = FileField('Upload images',
                     render_kw={'multiple': True}
  )


@app.route('/', methods=['POST', 'GET'])
def upload_page():
  form = UploadForm()
  fn_list = None 
  if form.validate_on_submit():
    fn_list = s3_upload()
  return render_template('upload.html', form=form, filenames=fn_list)


@app.route('/result/<image_name>')
def result(image_name):
  print('result for: {}'.format(image_name))
  if check_result(image_name):
    # return redirect('http://ec2-35-167-117-254.us-west-2.compute.amazonaws.com/efs/matcher/{}.html'.format(image_name), code=302)
    return redirect('https://s3-us-west-2.amazonaws.com/n4result/{}.html'.format(image_name), code=302)
  else:
    return 'still processing {}, please check in a few seconds.'.format(image_name)

if __name__ == '__main__':
    app.run(host = "0.0.0.0", port=app.config['PORT'])
    
