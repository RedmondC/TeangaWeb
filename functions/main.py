from flask import Flask, render_template, url_for

app = Flask(__name__)
app.config['DEBUG'] = False

@app.route("/")
def main():
    logo = url_for("static", filename="header_with_dara_knot.png")
    layered_screens = url_for("static", filename="layered_screens.png")
    google_badge = url_for("static", filename="GetItOnGooglePlay_Badge_Web_color_English.png")
    apple_badge = url_for("static", filename="Download_on_the_App_Store_Badge_US-UK_RGB_blk_092917.png")
    return render_template("index.html", logo=logo, layered_screens=layered_screens, google_badge=google_badge, apple_badge=apple_badge)