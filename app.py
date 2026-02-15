from flask import Flask, request, render_template_string
import swisseph as swe
import datetime
import os

app = Flask(__name__)

swe.set_sid_mode(swe.SIDM_LAHIRI)
flags = swe.FLG_SWIEPH | swe.FLG_SIDEREAL

ORB = 0.15

planets = {
    "Sun": swe.SUN,
    "Mercury": swe.MERCURY,
    "Venus": swe.VENUS,
    "Mars": swe.MARS,
    "Jupiter": swe.JUPITER,
    "Saturn": swe.SATURN,
    "Rahu": swe.MEAN_NODE,
    "Uranus": swe.URANUS,
    "Neptune": swe.NEPTUNE,
    "Pluto": swe.PLUTO
}

aspects = {
    0: "Conjunction 0",
    30: "Semi-Sextile 30",
    45: "Semi-Square 45",
    60: "Sextile 60",
    90: "Square 90",
    120: "Trine 120",
    150: "Quincunx 150",
    180: "Opposition 180"
}

def angle_diff(a, b):
    d = abs(a - b) % 360
    return min(d, 360 - d)

@app.route("/", methods=["GET", "POST"])
def home():
    result = []

    if request.method == "POST":
        date_input = request.form["date"]

        try:
            day, month, year = map(int, date_input.split("-"))
        except:
            return "Invalid format. Use DD-MM-YYYY"

        start_time = datetime.datetime(year, month, day, 9, 15)
        end_time   = datetime.datetime(year, month, day, 15, 30)

        current_time = start_time

        while current_time <= end_time:

            utc_time = current_time - datetime.timedelta(hours=5, minutes=30)

            jd_now = swe.julday(
                utc_time.year,
                utc_time.month,
                utc_time.day,
                utc_time.hour + utc_time.minute / 60
            )

            moon_deg = swe.calc_ut(jd_now, swe.MOON, flags)[0][0]

            for pname, pid in planets.items():

                planet_deg = swe.calc_ut(jd_now, pid, flags)[0][0]
                diff = angle_diff(moon_deg, planet_deg)

                for deg, aname in aspects.items():
                    if abs(diff - deg) <= ORB:
                        result.append(
                            f"{current_time.strftime('%H:%M')} — Moon {aname} {pname}"
                        )

                # KETU
                if pname == "Rahu":
                    ketu_deg = (planet_deg + 180) % 360
                    diff_ketu = angle_diff(moon_deg, ketu_deg)

                    for deg, aname in aspects.items():
                        if abs(diff_ketu - deg) <= ORB:
                            result.append(
                                f"{current_time.strftime('%H:%M')} — Moon {aname} Ketu"
                            )

            current_time += datetime.timedelta(minutes=1)

    return render_template_string("""
    <h2>🌙 Moon Intraday Aspect Scanner</h2>
    <form method="post">
        <input name="date" placeholder="DD-MM-YYYY">
        <button type="submit">Scan</button>
    </form>
    <hr>
    {% for r in result %}
        <p>{{ r }}</p>
    {% endfor %}
    """, result=result)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)



