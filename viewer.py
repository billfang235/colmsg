# Import modules
import os
from os.path import join
import sys
from pathlib import Path
import datetime
import pandas as pd
from flask import Flask, render_template, send_from_directory, request

colmsg_path = "\\\\wsl.localhost\\rhel9\\home\\zguo\\Downloads\\colmsg\\乃木坂46"


def file2date(filename: str):
    filename = Path(filename).stem
    dt = filename.split("_")[-1]
    dt = datetime.datetime.strptime(dt, "%Y%m%d%H%M%S")
    jpdelta = datetime.timedelta(hours=9)
    dt = dt + jpdelta
    return dt.__str__()

def file2prop(filename: str):
    stem, ext = filename.split('.')
    seq_num, datatype, dt = stem.split('_')
    dt = datetime.datetime.strptime(dt, "%Y%m%d%H%M%S")
    jpdelta = datetime.timedelta(hours=9)
    dt = dt + jpdelta
    return (seq_num, datatype, dt.__str__(), ext, filename)

# Create a Flask app
app = Flask(__name__)

# app.jinja_env.filters["join"] = join
# Define a route for showing files
@app.route("/show_file/<folder>/<filename>")
def show_file(folder, filename):
    # Send the file from the folder
    folder = os.path.join(colmsg_path, folder)
    return send_from_directory(folder, filename)


# Define a route for the home page
@app.route("/")
def index():
    # get the names of the subfolders in the static folder
    folders = os.listdir(colmsg_path)
    return render_template("index.html", folders=folders)

@app.route("/show")
def show():
    # get the name of the folder chosen by the user
    folder = request.args.get("folder")
    if folder:
        # Define a custom filter to read a file
        def read_file(filename):
            # Open the file in read mode
            # filename = folder + filename
            filename = os.path.join(colmsg_path, folder, Path(filename).name)
            with open(filename, "r", encoding="utf-8") as f:
                # Read the content of the file
                content = f.read()
                # Return the content of the file
                return content

        app.jinja_env.filters["read_file"] = read_file

        # get the names of the files in the chosen folder
        files = os.listdir(os.path.join(colmsg_path, folder))
        media = [f for f in files if f.endswith(".mp4") or f.endswith(".jpg") or f.endswith(".txt")]
        # Sort the media by their name
        media = sorted(media)[::-1]
        media = [file2prop(f) for f in media]
        df = pd.DataFrame(media, columns=['seq_num', 'datatype', 'datetime', 'ext', 'filename'])
        media_list = list()
        for grp_num, grp_df in df.groupby('seq_num', sort=False):
            if len(grp_df) == 1:
                grp_df = grp_df.iloc[0]
                media_list.append((grp_df.ext, grp_df.filename, grp_df.datetime, ''))
            else:
                assert grp_df['ext'].iloc[0] == 'txt'
                media_list.append(('multi', grp_df['filename'].iloc[1], grp_df['datetime'].iloc[1],
                                   read_file(grp_df['filename'].iloc[0])))

        # media_date = [file2date(f) for f in media]
        # media = list(zip(media, media_date))

        # Render an HTML template with the media
        return render_template("show.html", folder=folder, media=media_list)
    else:
        return "Please choose a folder."

# Run the app
if __name__ == "__main__":
    # app.run(debug=True)
    app.run(debug=False, host="0.0.0.0", port=80)