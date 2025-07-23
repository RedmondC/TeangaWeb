from flask import render_template, url_for


def render_index():
    logo = url_for("static", filename="header_with_dara_knot.png")
    panel = url_for("static", filename="panel.png")
    layered_screens = url_for("static", filename="layered_screens.png")
    google_badge = url_for(
        "static", filename="GetItOnGooglePlay_Badge_Web_color_English.png"
    )
    apple_badge = url_for(
        "static", filename="Download_on_the_App_Store_Badge_US-UK_RGB_blk_092917.png"
    )

    return render_template(
        "index.html",
        logo=logo,
        panel=panel,
        layered_screens=layered_screens,
        irish_information=generate_information(
            google_badge=google_badge,
            google_alt="Faigh é ar Google Play",
            apple_badge=apple_badge,
            apple_alt="Faigh é ar an t-siopa aip Apple",
            welcome="Fáilte go dtí an suíomh gréasáin Teanga!",
            contact="Má go bhfuil aon ceist nó gearán agat, ná bíodh aon drogall ort r-post a chur orainn ar ",
            download_links="Chun áir aip a íoslódáil, lean na nascanna seo:",
            disclaimer="Dála an scéal, tá ár aip a fhad níos gleoite ná an suíomh seo!",
        ),
        english_information=generate_information(
            google_badge=google_badge,
            google_alt="Get it on Google Play",
            apple_badge=apple_badge,
            apple_alt="Get it on the Apple app store",
            welcome="Welcome to the Teanga website!",
            contact="If you have any questions or complaints please don't hesitate to email us at ",
            download_links="To download our App please follow these links:",
            disclaimer="By the way, our app is a lot nicer than this website!",
        ),
    )


def generate_information(
    google_badge: str,
    google_alt: str,
    apple_badge: str,
    apple_alt: str,
    welcome: str,
    contact: str,
    download_links: str,
    disclaimer: str,
):
    badges = render_template(
        "badges.html",
        google_badge=google_badge,
        google_alt=google_alt,
        apple_badge=apple_badge,
        apple_alt=apple_alt,
    )

    return render_template(
        "information.html",
        welcome=welcome,
        contact=contact,
        download_links=download_links,
        disclaimer=disclaimer,
        badges=badges,
    )
