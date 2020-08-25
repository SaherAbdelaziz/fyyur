#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for, jsonify, abort
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from flask_migrate import Migrate
import sys
from datetime import datetime
from sqlalchemy.orm import backref

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# TODO: connect to a local postgresql database
# done

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#


class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))

    website = db.Column(db.String(120))
    seeking_talent = db.Column(db.Boolean)
    seeking_description = db.Column(db.String())

    # artists = db.relationship("Artist", secondary="Show")

    # TODO: implement any missing fields, as a database migration using Flask-Migrate


class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))

    seeking_venue = db.Column(db.Boolean)
    seeking_description = db.Column(db.String())
    website = db.Column(db.String(120))

    # venues = db.relationship("Venue", secondary="Show")

    # TODO: implement any missing fields, as a database migration using Flask-Migrate
    # done expet genres

# TODO Implement Show and Artist models, and complete all model relationships and properties, #
# as a database migration.


class Show(db.Model):
    __tablename__ = 'Show'
    id = db.Column(db.Integer, primary_key=True)
    venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id'), nullable=False)
    artist_id = db.Column(db.Integer, db.ForeignKey(
        'Artist.id'), nullable=False)
    start_time = db.Column(db.DateTime, default=datetime.utcnow())

    artist = db.relationship(Artist, backref=backref(
        "Show", cascade="all, delete-orphan"))
    venue = db.relationship(Venue, backref=backref(
        "Show", cascade="all, delete-orphan"))

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#


def format_datetime(value, format='medium'):
    date = dateutil.parser.parse(value)
    if format == 'full':
        format = "EEEE MMMM, d, y 'at' h:mma"
    elif format == 'medium':
        format = "EE MM, dd, y h:mma"
    return babel.dates.format_datetime(date, format)


app.jinja_env.filters['datetime'] = format_datetime


def datetimeformat(value, format='%H:%M / %d-%m-%Y'):
    return value.strftime(format)


app.jinja_env.filters['datetimeformat'] = datetimeformat
#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#


@app.route('/')
def index():
    return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
    # TODO: replace with real venues data.
    #       num_shows should be aggregated based on number of upcoming shows per venue.
    # done

    areas = Venue.query.with_entities(Venue.city, Venue.state).distinct()
    venues = Venue.query.all()
    aAndv = {}
    listOfAreasOfVenues = []
    for a in areas:
        aAndv = {
            'city': a.city,
            'state': a.state,
            'venues': Venue.query.filter_by(city=a.city, state=a.state).all()
        }
        listOfAreasOfVenues.append(aAndv.copy())

    return render_template('pages/venues.html', areas=listOfAreasOfVenues)


@app.route('/venues/search', methods=['POST'])
def search_venues():
    # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
    # seach for Hop should return "The Musical Hop".
    # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
    # done

    word = request.form.get('search_term', '')
    data = Venue.query.filter(Venue.name.ilike(f"%{word}%"))
    count = data.count()
    res = {
        "count": count,
        "data": data.all()
    }
    return render_template('pages/search_venues.html', results=res, search_term=request.form.get('search_term', ''))


@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
    # shows the venue page with the given venue_id
    # TODO: replace with real venue data from the venues table, using venue_id
    # done

    venueAndShowsList = db.session.query(Venue, Show).outerjoin(
        Show, Venue.id == Show.venue_id).filter(Venue.id == venue_id).all()

    venue = venueAndShowsList[0].Venue

    venue.upcoming_shows_count = 0
    venue.past_shows_count = 0

    venue.upcoming_shows = []
    venue.past_shows = []

    dateTimeNow = datetime.now()

    for sh in venueAndShowsList:
        if (sh.Show != None):
            if (sh.Show.start_time > dateTimeNow):
                venue.upcoming_shows_count += 1
                venue.upcoming_shows.append(sh.Show)
            else:
                venue.past_shows_count += 1
                venue.past_shows.append(sh.Show)

    # data = list(filter(lambda d: d['id'] == venue_id, [data1, data2, data3]))[0]
    # data = Venue.query.get(venue_id)
    return render_template('pages/show_venue.html', venue=venue)

#  Create Venue
#  ----------------------------------------------------------------


@app.route('/venues/create', methods=['GET'])
def create_venue_form():
    form = VenueForm()
    return render_template('forms/new_venue.html', form=form)


@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
    # TODO: insert form data as a new Venue record in the db, instead
    # TODO: modify data to be the data object returned from db insertion
    # done
    form = VenueForm(request.form)
    if not form.validate_on_submit():
        return render_template('forms/new_venue.html', form=form)
    error = False
    body = {}
    is_checked = False
    if request.method == "POST":
        is_checked = request.form.get("seeking_talent", False)

        if is_checked == 'y':
            is_checked = True
    try:
        venue = Venue(
            name=request.form['name'], city=request.form['city'], state=request.form['state'],
            image_link=request.form['image_link'],
            phone=request.form['phone'], address=request.form['address'],
            website=request.form['website'],
            seeking_talent=is_checked,
            seeking_description=request.form['seeking_description'],
            # , genres=request.form['genres']
            facebook_link=request.form['facebook_link']
        )

        db.session.add(venue)
        db.session.commit()

        # on successful db insert, flash success
        flash('Venue ' + request.form['name'] + ' was successfully listed!')
    except:
        error = True
        db.session.rollback()
        print(sys.exc_info())
        # TODO: on unsuccessful db insert, flash an error instead.
        flash('An error occurred. Venue ' +
              request.form['name'] + ' could not be listed.')
    finally:
        db.session.close()
    if error:
        abort(400)

    else:
        # return jsonify(body)
        return render_template('pages/home.html')


@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
    # TODO: Complete this endpoint for taking a venue_id, and using
    # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
    error = False

    try:
        Venue.query.filter_by(id=venue_id).delete()

        db.session.commit()

    except:
        error = True
        db.session.rollback()

    finally:
        db.session.close()

    if error:
        abort(400)

    # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
    # clicking that button delete it from the db then redirect the user to the homepage
    return None

#  Artists
#  ----------------------------------------------------------------


@app.route('/artists')
def artists():
    # TODO: replace with real data returned from querying the database
    # done

    data = Artist.query.all()
    return render_template('pages/artists.html', artists=data)


@app.route('/artists/search', methods=['POST'])
def search_artists():
    # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
    # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
    # search for "band" should return "The Wild Sax Band".
    # done
    word = request.form.get('search_term', '')
    data = Artist.query.filter(Artist.name.ilike(f"%{word}%"))
    count = data.count()
    res = {
        "count": count,
        "data": data.all()
    }
    return render_template('pages/search_artists.html', results=res, search_term=request.form.get('search_term', ''))


@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
    # shows the venue page with the given venue_id
    # TODO: replace with real venue data from the venues table, using venue_id
    # done

    artistAndShowsList = db.session.query(Artist, Show).outerjoin(
        Show, Artist.id == Show.artist_id).filter(Artist.id == artist_id).all()

    artist = artistAndShowsList[0].Artist

    artist.upcoming_shows_count = 0
    artist.past_shows_count = 0

    artist.upcoming_shows = []
    artist.past_shows = []

    dateTimeNow = datetime.now()

    for sh in artistAndShowsList:
        if (sh.Show != None):
            if (sh.Show.start_time > dateTimeNow):
                artist.upcoming_shows_count += 1
                artist.upcoming_shows.append(sh.Show)
            else:
                artist.past_shows_count += 1
                artist.past_shows.append(sh.Show)

    # artist = Artist.query.first()
    # data = list(filter(lambda d: d['id'] ==artist_id, allData))[0]
    return render_template('pages/show_artist.html', artist=artist)

#  Update
#  ----------------------------------------------------------------


@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
    form = ArtistForm()
    artist = Artist.query.get(artist_id)
    # TODO: populate form with fields from artist with ID <artist_id>
    # done in view
    return render_template('forms/edit_artist.html', form=form, artist=artist)


@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
    # TODO: take values from the form submitted, and update existing
    # artist record with ID <artist_id> using the new attributes
    form = ArtistForm(request.form)
    artist = Artist.query.get(artist_id)
    if not form.validate_on_submit():
        return render_template('forms/edit_artist.html', form=form, artist=artist)

    artist.name = form.name.data
    artist.city = form.city.data
    artist.state = form.state.data
    artist.phone = form.phone.data
    artist.image_link = form.image_link.data
    artist.genres = form.genres.data
    artist.facebook_link = form.facebook_link.data
    artist.seeking_venue = form.seeking_venue.data
    artist.seeking_description = form.seeking_description.data
    artist.website = form.website.data
    try:
        db.session.add(artist)
        db.session.commit()
    except:
        db.session.rollback()
        error = True
    finally:
        db.session.close()

    return redirect(url_for('show_artist', form=form, artist=artist))


@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
    form = VenueForm()
    venue = Venue.query.get(venue_id)
    # TODO: populate form with values from venue with ID <venue_id>
    # done
    return render_template('forms/edit_venue.html', form=form, venue=venue)


@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
    # TODO: take values from the form submitted, and update existing
    # venue record with ID <venue_id> using the new attributes
    # done
    form = VenueForm(request.form)
    venue = Venue.query.get(venue_id)
    if not form.validate_on_submit():
        return render_template('forms/edit_venue.html', form=form, venue=venue)

    venue.name = form.name.data
    venue.city = form.city.data
    venue.state = form.state.data
    venue.phone = form.phone.data
    venue.image_link = form.image_link.data
    venue.facebook_link = form.facebook_link.data
    venue.seeking_talent = form.seeking_talent.data
    venue.seeking_description = form.seeking_description.data
    venue.website = form.website.data

    try:
        db.session.add(venue)
        db.session.commit()
    except:
        db.session.rollback()
        error = True
    finally:
        db.session.close()

    return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------


@app.route('/artists/create', methods=['GET'])
def create_artist_form():
    form = ArtistForm()
    return render_template('forms/new_artist.html', form=form)


@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
    # called upon submitting the new artist listing form
    # TODO: insert form data as a new Venue record in the db, instead
    # TODO: modify data to be the data object returned from db insertion
    # done
    form = ArtistForm(request.form)
    if not form.validate_on_submit():
        return render_template('forms/new_artist.html', form=form)
    error = False
    body = {}
    is_checked = False
    if request.method == "POST":
        is_checked = request.form.get("seeking_venue", False)

        if is_checked == 'y':
            is_checked = True
    try:
        artist = Artist(
            name=request.form['name'], city=request.form['city'], state=request.form['state'],
            image_link=request.form['image_link'],
            phone=request.form['phone'], genres=request.form['genres'],
            website=request.form['website'],
            seeking_venue=is_checked,
            # seeking_venue=str(form.checkbox.data),
            seeking_description=request.form['seeking_description'],
            facebook_link=request.form['facebook_link']
        )

        db.session.add(artist)
        db.session.commit()

        # on successful db insert, flash success
        flash('Artist ' + request.form['name'] + ' was successfully listed!')
    except:
        error = True
        db.session.rollback()
        print(sys.exc_info())
        # TODO: on unsuccessful db insert, flash an error instead.
        flash('An error occurred. Artist ' +
              request.form['name'] + ' could not be listed.')
    finally:
        db.session.close()
    if error:
        abort(400)

    else:
        # return jsonify(body)
        return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
    # displays list of shows at /shows
    # TODO: replace with real venues data.
    #       num_shows should be aggregated based on number of upcoming shows per venue.
    # done

    data = Show.query.all()
    return render_template('pages/shows.html', shows=data)


@app.route('/shows/create')
def create_shows():
    # renders form. do not touch.
    form = ShowForm()
    return render_template('forms/new_show.html', form=form)


@app.route('/shows/create', methods=['POST'])
def create_show_submission():
    # called to create new shows in the db, upon submitting new show listing form
    # TODO: insert form data as a new Show record in the db, instead
    # done
    form = ShowForm(request.form)
    if not form.validate_on_submit():
        return render_template('forms/new_show.html', form=form)
    error = False
    body = {}
    try:
        show = Show(
            artist_id=form.artist_id.data,
            venue_id=form.venue_id.data,

            start_time=form.start_time.data,
        )

        db.session.add(show)
        db.session.commit()

        # on successful db insert, flash success
        flash('Show was successfully listed!')
    except:
        error = True
        db.session.rollback()
        print(sys.exc_info())
        # TODO: on unsuccessful db insert, flash an error instead.
        flash('An error occurred while inserting show')
    finally:
        db.session.close()
    if error:
        abort(400)

    else:
        # return jsonify(body)
        return render_template('pages/home.html')


@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404


@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
