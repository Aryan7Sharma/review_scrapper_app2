from flask import Flask, render_template, request,jsonify
from flask_cors import CORS,cross_origin
import requests
from bs4 import BeautifulSoup as bs
from urllib.request import urlopen as uReq
from local_logger import logss as lg
import mongo_db
import pandas as pd
app = Flask(__name__)

@app.route('/',methods=['GET'])  # route to display the home page
@cross_origin()
def homePage():
    return render_template("index.html")

@app.route('/review',methods=['POST','GET']) # route to show the review comments in a web UI
@cross_origin()
def index():
    if request.method == 'POST':
        try:
            searchString = request.form['content'].replace(" ","")
            number_of_prod = request.form['number']
            no_of_reviews = int(number_of_prod)
            flipkart_url = "https://www.flipkart.com/search?q=" + searchString
            lg().info("flipkart url -- %s", flipkart_url)
            uClient = uReq(flipkart_url)
            flipkartPage = uClient.read() #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
            uClient.close()
            flipkart_html = bs(flipkartPage, "html.parser")
            bigboxes = flipkart_html.findAll("div", {"class": "_1AtVbE col-12-12"})
            del bigboxes[0:3]
            box = bigboxes[0]
            productLink = "https://www.flipkart.com" + box.div.div.div.a['href']
            lg().info("product link captured -- %s", productLink)
            prodRes = requests.get(productLink)
            prodRes.encoding='utf-8'
            prod_html = bs(prodRes.text, "html.parser")

            comment_section_pages_section = prod_html.find('div', {'class': "col JOpGWq"})
            comment_section_pages_url = comment_section_pages_section.findAll('a')[-1]['href']
            comment_section_pages_url = "https://www.flipkart.com"+comment_section_pages_url+"&page=0"
            header = {"Index": [], "Product": [], "Name": [], "Location": [], "Rating": [], "CommentHead": [],
                          "Comment": [], "Verification": [], "Likes": [], "Dislikes": [], "URL": []}
            df = pd.DataFrame(header)
            reviews = []
            index = 1
            pages = no_of_reviews//10
            every_page_url = comment_section_pages_url
            lg().info("Comment Section Url is Captured -- %s", comment_section_pages_url)
            for i in range(1, pages+5):
                every_page_url = every_page_url[:-1]+str(i)
                lg().info("every page url index--%s, --%s", index, every_page_url)
                page_reqs = requests.get(every_page_url)
                page_reqs.encoding = 'utf-8'
                html_pages_ofcomments = bs(page_reqs.text, "html.parser")
                commentboxes = html_pages_ofcomments.find_all('div', {'class': "col _2wzgFH K0kLPL"})
                for commentbox in commentboxes:

                    # name
                    try:
                        #name.encode(encoding='utf-8')
                        lg().info("scrapping name of page %s", i)
                        name = commentbox.find('p', {'class':'_2sc7ZR _2V5EHH'}).text

                    except Exception as e:
                        name = 'No Name'
                        lg().exception(e)

                    #location
                    try:
                        lg().info("scrapping locationOf_user of page %s", i)
                        # rating.encode(encoding='utf-8')
                        locaton_section = commentbox.find('p', {'class': '_2mcZGG'}).text
                        locaton = locaton_section.split(',')[-1]

                    except Exception as e:
                        locaton = 'No Location'
                        lg().exception(e)

                    #Ratings
                    try:
                        lg().info("scrapping rating of page %s", i)
                        rating = commentbox.div.div.text

                    except Exception as e:
                        rating = 'No Rating'
                        lg().exception(e)

                    #Comment Heading
                    try:
                        lg().info("scrapping comment heading of page %s", i)
                        commentHead = commentbox.div.p.text.strip()

                    except Exception as e:
                        commentHead = 'No Comment Heading'
                        lg().exception(e)

                    #Comment
                    try:
                        lg().info("scrapping long_comment of page %s", i)
                        comtag = commentbox.find_all('div', {'class': 't-ZTKy'})
                        # comtag is a list
                        custComment = comtag[0].text

                    except Exception as e:
                        custComment = "Sorry Comment is not Available"
                        lg().exception(e)

                    #Verified Customer or Not
                    try:
                        lg().info("scrapping verified or Not of page %s", i)
                        verified = commentbox.find('p', {'class': '_2mcZGG'}).span.text

                    except Exception as e:
                        verified = 'Not Verified'
                        lg().exception(e)

                    #Likes on the comment
                    try:
                        lg().info("scrapping Likes on the comments of page %s", i)
                        likes = commentbox.find('div', {'class': '_1e9_Zu'}).span.text

                    except Exception as e:
                        lg().exceptione(e)
                        likes = '0'

                    # Dislikes on the comment
                    try:
                        lg().info("scrapping Dislikes on the comments of page %s", i)
                        dislikes = commentbox.find('div', {'class': '_1LmwT9 pkR4jH'}).span.text

                    except Exception as e:
                        lg().exceptione(e)
                        dislikes = '0'

                    mydict = {"Index": index, "Product": searchString, "Name": name, "Location": locaton, "Rating": rating, "CommentHead": commentHead,
                          "Comment": custComment, "Verification": verified, "Likes": likes, "Dislikes": dislikes, "URL": every_page_url}
                    reviews.append(mydict)
                    df = df.append(mydict, ignore_index=True)
                    index+=1
                if index >= no_of_reviews:
                    break

            df.to_csv('static/Scrapped_data.csv', index=0)
            return render_template('results.html', reviews=reviews[0:no_of_reviews])
        except Exception as e:
            lg().info('The Exception message is: ', e)
            return 'something is wrong'
    # return render_template('results.html')

    else:
        return render_template('index.html')

@app.route('/feedback',methods=['POST', 'GET'])  # route to display the home page
@cross_origin()
def feedbacks():
    return render_template("feedback.html")

@app.route('/feedback/submit',methods=['POST', 'GET'])  # route to display the home page
@cross_origin()
def submit():
    if request.method == 'POST':
        try:
            firstname = request.form['firstname']
            lastname = request.form['lastname']
            mailid = request.form['mailid']
            country = request.form['country']
            message = request.form['messages']

            # merging name
            full_name = firstname+" "+lastname
            data_dict = {'Name': full_name, 'Mail_ID': mailid, 'Country': country, 'Feedback_Message' : message}
            mongo_db.dump_feedback(data_dict)
            lg().info("Feedback dumped in mongodb successfully ")
            return render_template("submit.html")
        except Exception as e:
            lg().exception(e)
    else:
        return render_template("index.html")


if __name__ == "__main__":
    #app.run(host='127.0.0.1', port=8001, debug=True)
	app.run(debug=True)
