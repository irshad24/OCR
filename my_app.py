from flask import Flask
from flask import request,render_template,send_file
import os
from easyocr import Reader
import argparse
import cv2
import pandas as pd
import fitz
o_file =' '
a=[]## START OF PYTHON VARIABLE
b=[]
a1=''
a2=''
arr=[]
c=''
d=["Full Name","ENTRY PERMIT NO","UID NO:","Date Of Issue","Place Of Issue","Valid Until","Nationality","Place of Birth","Date of Birth","Passport Type","Passport No","Profession","Accompanied By","Sponsor","Sponsor Address"]
length_d=len(d)
e=[] ## END OF PYTHON VARIBLE
k=''


UPLOADER_FOLDER=''
app=Flask(__name__)
app.config['UPLOADER_FOLDER']=UPLOADER_FOLDER

@app.route('/')
@app.route('/index',methods=['GET','POST'])
def index():
    if request.method=="POST":
        def convert_pdf2csv(input_file:str):
            global k,c
            file_path = input_file## START OF PYTHON PROGRAM 
            doc = fitz.open(file_path)  # open document
            for i, page in enumerate(doc):
                zoom = 6    # zoom factor
                mat = fitz.Matrix(zoom, zoom)
                pix = page.get_pixmap(matrix = mat) # render page to an image
                pix.save("test.jpg") 
                break
            # Loop over pages and render
            def cleanup_text(text):
                # strip out non-ASCII text so we can draw the text on the image
                # using OpenCV
                return "".join([c if ord(c) < 128 else "" for c in text]).strip()
            # construct the argument parser and parse the arguments
            ap = argparse.ArgumentParser()
            ap.add_argument("-i", "--image", required=False,
                help="path to input image to be OCR'd")
            ap.add_argument("-l", "--langs", type=str, default="en",
                help="comma separated list of languages to OCR")
            ap.add_argument("-g", "--gpu", type=int, default=-1,
                help="whether or not GPU should be used")
            args = vars(ap.parse_args())
            # break the input languages into a comma separated list
            langs = args["langs"].split(",")
            print("[INFO] OCR'ing with the following languages: {}".format(langs))
            # load the input image from disk 
            image = cv2.imread("test.jpg")

            # OCR the input image using EasyOCR
            print("[INFO] OCR'ing input image...")
            reader = Reader(langs,verbose=False)
            results = reader.readtext(image)
            # loop over the results
            for (bbox, text, prob) in results:
                # display the OCR'd text and associated probability
                #print("[INFO] {:.4f}: {}".format(prob, text))
                arr.append(text)
                
                # unpack the bounding box
                (tl, tr, br, bl) = bbox
                tl = (int(tl[0]), int(tl[1]))
                tr = (int(tr[0]), int(tr[1]))
                br = (int(br[0]), int(br[1]))
                bl = (int(bl[0]), int(bl[1]))
                # cleanup the text and draw the box surrounding the text along
                # with the OCR'd text itself
                text = cleanup_text(text)
                
                cv2.rectangle(image, tl, br, (0, 255, 0), 2)
                cv2.putText(image, text, (tl[0], tl[1] - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)

            # show the output image
            for index, item in enumerate(arr):
                if item.startswith("Full Name"):
                    a.append("Full Name")
                    b.append(arr[index+1])
                    global c
                    c=arr[index+1]
                elif item.startswith("ENTRY PERMIT NO"):	
                    a.append("ENTRY PERMIT NO")
                    b.append(arr[index+1])
                elif item.startswith("Allowed"):	
                    a.append("UID NO:")
                    b.append(arr[index-2])	
                elif item.startswith("Date & Place of Issue"):
                    a.append("Date Of Issue")
                    a1=arr[index+1].split()[0]
                    a2=arr[index+1].split()[-1]
                    b.append(a1)
                    a.append("Place Of Issue")
                    b.append(a2)
                elif item.startswith("Valid Until"):
                    a.append("Valid Until")
                    b.append(arr[index+1])
                elif item.startswith("Nationality"):
                    a.append("Nationality")
                    b.append(arr[index+1])
                elif item.startswith("Place "):
                    a.append("Place of Birth")
                    b.append(arr[index+1])
                elif item.startswith("Date of Birth"):
                    a.append("Date of Birth")
                    b.append(arr[index+1])	
                elif item.startswith("Passport No"):
                    a.append("Passport Type")
                    b.append(arr[index+1])
                    a.append("Passport No")
                    b.append(arr[index+2])
                elif item.startswith("Profession"):
                    a.append("Profession")
                    b.append(arr[index+1])	
                elif item.startswith("Accompanied"):
                    a.append("Accompanied By")
                    b.append(arr[index+2])		
                elif item.startswith("Name"):
                    a.append("Sponsor")
                    b.append(arr[index+1])
                elif item.startswith("TEL"):
                    a.append("Sponsor Address")
                    b.append(arr[index])			
            result_1 = list(set(d).difference(a))
            for i in range(len(d)-len(a)):
                a.append(result_1[i])
                b.append(" ")   

            df = pd.DataFrame(list(zip(a,b)))
            print(length_d)
            df2 = df.head(length_d)
            print(df2)
            global o_file
            o_file = str(c)+ ' Visa.csv'	
            df2.to_csv(o_file) ## END OF THE PYTHON CODE
            return o_file
           
            
            
        file=request.files['filename']
        if file.filename!='':
           file.save(os.path.join(app.config['UPLOADER_FOLDER'],file.filename))
           input_file=file.filename
           convert_pdf2csv(input_file)
           return render_template("csv.html")
    return render_template("index.html")


@app.route('/csv',methods=['GET','POST'])
def csv():
    if request.method=="POST":
        return send_file(o_file,as_attachment=True)
    return  render_template("index.html")
if __name__=="__main__":
    app.debug=True
    app.run()
