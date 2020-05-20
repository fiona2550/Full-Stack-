#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func, inspect
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from flask_migrate import Migrate
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)
migrate = Migrate(app, db)


Show = db.Table('Show', 
    db.Column('Venue_id', db.Integer, db.ForeignKey('Venue.id'), primary_key=True),
    db.Column('Artist_id', db.Integer, db.ForeignKey('Artist.id'), primary_key=True),
	db.Column('start_time', db.DateTime)
)
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
	
	seeking_talent = db.Column(db.Boolean)
	seeking_description = db.Column(db.String(500))
	website = db.Column(db.String(120))
	genres = db.Column(db.ARRAY(db.String))
	venues = db.relationship('Artist', secondary=Show, backref=db.backref('shows', lazy='joined'))
	#def __repr__(self):
        #return 'Venue Id:{} | Name: {}'.format(self.id, self.name)
		
		
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
	genres = db.Column(db.ARRAY(db.String())) # To store multiple Genres, I decided to create an Array Column with String as Datatype
	seeking_description = db.Column(db.String(500))

    # TODO: implement any missing fields, as a database migration using Flask-Migrate

	def __repr__(self):
		return f'<Artist {self.id} {self.name}>'
		
# TODO: connect to a local postgresql database
def get_dict_list_from_result(result):
	#https://stackoverflow.com/questions/48232222/how-to-deal-with-sqlalchemy-util-collections-result
	list_dict = []
	for i in result:
		i_dict = i._asdict()  
		list_dict.append(i_dict)
	return list_dict
	
def object_as_dict(obj):
	#Converts SQLALchemy Query Results to Dict
	#Makes use of the SQLAlchemy inspection system (https://docs.sqlalchemy.org/en/13/core/inspection.html)

	return {c.key: getattr(obj, c.key) for c in inspect(obj).mapper.column_attrs}
#----------------------------------------------------------------------------#
#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
	date = dateutil.parser.parse(value)
	if format == 'full':
		format="EEEE MMMM, d, y 'at' h:mma"
	elif format == 'medium':
		format="EE MM, dd, y h:mma"
	return babel.dates.format_datetime(date, format)

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
#	Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')


#	Venues
#	----------------------------------------------------------------

@app.route('/venues')
def venues():
	# TODO: replace with real venues data.
	#       num_shows should be aggregated based on number of upcoming shows per venue.
 
	groupby_venues_result = (db.session
		.query( Venue.city, Venue.state )
        .group_by( Venue.city, Venue.state )
 )
	

	data=get_dict_list_from_result(groupby_venues_result)
	
	print(Venue.query.with_entities(Venue.id, Venue.name, Venue.state).filter_by(city = 'Philadelphia').all())
	for area in data:
		area['venues'] = [object_as_dict(ven) for ven in Venue.query.filter_by(city = area['city']).all()]
		for ven in area['venues']:
			
			ven['num_upcoming_shows'] = db.session.query(func.count(Show.c.Venue_id)).filter(Show.c.Venue_id == ven['id']).filter(Show.c.start_time > datetime.now()).all()[0][0]
	#print(data)
	return render_template('pages/venues.html', areas=data)

	
@app.route('/venues/search', methods=['POST'])
def search_venues():
	search_term=request.form.get('search_term', '')
	#search_term=request.get_json()['search_term']
	search_venues_count = (db.session.query(
    Venue.id)
    .filter(Venue.name.contains(search_term))
	.count())
	search_venues_result = Venue.query.filter(Venue.name.contains(search_term)).all()
	print(search_venues_count)
	response={
    "count": search_venues_count,
    "data": search_venues_result}
	
	return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
	# shows the venue page with the given venue_id
	# TODO: replace with real venue data from the venues table, using venue_id
	venue = Venue.query.get(venue_id)
	venue.past_shows = (db.session.query(
	Artist.id.label("artist_id"), 
	Artist.name.label("artist_name"), 
	Artist.image_link.label("artist_image_link"), 
    Show)
    .filter(Show.c.Venue_id == venue_id)
    .filter(Show.c.Artist_id == Artist.id)
    .filter(Show.c.start_time <= datetime.now())
    .all())
  
	venue.upcoming_shows = (db.session.query(
	Artist.id.label("artist_id"), 
	Artist.name.label("artist_name"), 
	Artist.image_link.label("artist_image_link"), 
    Show)
    .filter(Show.c.Venue_id == venue_id)
    .filter(Show.c.Artist_id == Artist.id)
    .filter(Show.c.start_time > datetime.now())
    .all())

	venue.past_shows_count = (db.session.query(
	Venue_id)
    .filter(Show.c.Venue_id == venue_id)
    .filter(Show.c.start_time < datetime.now())
    .count())

	venue.upcoming_shows_count = (db.session.query(
	func.count(Show.c.Venue_id))
    .filter(Show.c.Venue_id == venue_id)
    .filter(Show.c.start_time > datetime.now())
    .count())

	return render_template('pages/show_venue.html', venue=venue)

#	Create Venue
#	----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
	form = VenueForm()
	return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
	# TODO: insert form data as a new Venue record in the db, instead
	# TODO: modify data to be the data object returned from db insertion
	form = VenueForm(request.form) # Initialize form instance with values from the request
	flashType = 'danger' # Initialize flashType to danger. Either it will be changed to "success" on successfully db insert, or in all other cases it should be equal to "danger"
	if form.validate():
		try:
      # Create a new instance of Venue with data from VenueForm
			newVenue = Venue(
				name = request.form['name'],
				city = request.form['city'],
				state = request.form['state'],
				address = request.form['address'],
				phone = request.form['phone'],
				genres = request.form.getlist('genres'),
				facebook_link = request.form['facebook_link']
			)
			db.session.add(newVenue)
			db.session.commit()
		  # on successful db insert, flash success
			flashType = 'success'
			flash('Venue {} was successfully listed!'.format(newVenue.name))
		except: 
		  # TODO DONE: on unsuccessful db insert, flash an error instead.
		  flash('An error occurred due to database insertion error. Venue {} could not be listed.'.format(request.form['name']))
		finally:
		  # Always close session
		  db.session.close()
	else:
		flash(form.errors) # Flashes reason, why form is unsuccessful (not really pretty)
		flash('An error occurred due to form validation. Venue {} could not be listed.'.format(request.form['name']))
	  
	return render_template('pages/home.html', flashType = flashType)


@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
	# TODO: Complete this endpoint for taking a venue_id, and using
	# SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
	
	# BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
	# clicking that button delete it from the db then redirect the user to the homepage
	try:
		Venue.query.filter_by(id=venue_id).delete()
		db.session.commit()
	except:
		db.session.rollback()

		return jsonify({ 'success': False })
	finally:

		db.session.close()
	return jsonify({ 'success': True })
	return None

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
	# TODO: replace with real data returned from querying the database
	artists = Artist.query.all()
	return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
	# TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
	# seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
	# search for "band" should return "The Wild Sax Band".
  
	search_term=request.form.get('search_term', '')

	search_artist_count = db.session.query(Artist.id).filter(Artist.name.contains(search_term)).count()
	search_artist_result = Artist.query.filter(Artist.name.contains(search_term)).all()
	response={
    "count": search_artist_count,
    "data": search_artist_result
  }
	return render_template('pages/search_artists.html', results=response, search_term=search_term)
  
@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
	# shows the venue page with the given venue_id
	# TODO: replace with real venue data from the venues table, using venue_id
	# Step 1: Get single Artist
	artist = Artist.query.get(artist_id)

	# Step 2: Get Past Shows
	artist.past_shows = (db.session.query(
    Venue.id.label("venue_id"), 
    Venue.name.label("venue_name"), 
    Venue.image_link.label("venue_image_link"), 
    Show)
    .filter(Show.c.Artist_id == artist_id)
    .filter(Show.c.Venue_id == Venue.id)
    .filter(Show.c.start_time <= datetime.now())
    .all())
  
	# Step 3: Get Upcomming Shows
	artist.upcoming_shows = (db.session.query(
    Venue.id.label("venue_id"), 
    Venue.name.label("venue_name"), 
    Venue.image_link.label("venue_image_link"), 
    Show)
    .filter(Show.c.Artist_id == artist_id)
    .filter(Show.c.Venue_id == Venue.id)
    .filter(Show.c.start_time > datetime.now())
    .all())

	# Step 4: Get Number of past Shows
	artist.past_shows_count = (db.session.query(
    Show.c.Artist_id)
    .filter(Show.c.Artist_id == artist_id)
    .filter(Show.c.start_time < datetime.now())
    .count())
  
	# Step 5: Get Number of Upcoming Shows
	artist.upcoming_shows_count = (db.session.query(
    Show.c.Artist_id)
    .filter(Show.c.Artist_id == artist_id)
    .filter(Show.c.start_time > datetime.now())
    .count())

	return render_template('pages/show_artist.html', artist=artist)


#	Update
#	----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
	form = ArtistForm()
  

	# Get single artist entry
	artist = Artist.query.get(artist_id)

	# Pre Fill form with data
	form.name.data = artist.name
	form.city.data = artist.city
	form.state.data = artist.state
	form.phone.data = artist.phone
	form.genres.data = artist.genres
	form.facebook_link.data = artist.facebook_link

	# TODO DONE: populate form with fields from artist with ID <artist_id>
	return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
	# TODO: take values from the form submitted, and update existing
	# artist record with ID <artist_id> using the new attributes
	artist = Venue.query.get(artist_id)
	artist.name = request.form['name'],
	artist.city = request.form['city'],
	artist.state = request.form['state'],
	artist.phone = request.form['phone'],
	artist.genres = request.form['genres'],
	artist.facebook_link = request.form['facebook_link']
	db.session.add(artist)
	db.session.commit()
	db.session.close()
	return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
	form = VenueForm()
	venue = Venue.query.get(venue_id)

	# Pre Fill form with data
	form.name.data = venue.name
	form.city.data = venue.city
	form.state.data = venue.state
	form.address.data = venue.address
	form.phone.data = venue.phone
	form.genres.data = venue.genres
	form.facebook_link.data = venue.facebook_link

	# TODO: populate form with values from venue with ID <venue_id>
	return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
	# TODO: take values from the form submitted, and update existing
	# venue record with ID <venue_id> using the new attributes
	venue = Venue.query.get(venue_id)
	venue.name = request.form['name'],
	venue.city = request.form['city'],
	venue.state = request.form['state'],
	venue.address = request.form['address'],
	venue.phone = request.form['phone'],
	venue.genres = request.form.getlist('genres'),
	venue.facebook_link = request.form['facebook_link']
	db.session.add(venue)
	db.session.commit()
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
	form = ArtistForm(request.form)
	flashType = 'danger'
	if form.validate():
		try:
      # Create a new instance of Artist with data from ArtistForm
			newArtist = Artist(
				name = request.form['name'],
				city = request.form['city'],
				state = request.form['state'],
				phone = request.form['phone'],
				facebook_link = request.form['facebook_link'],
				genres = request.form.getlist('genres')
				)
			db.session.add(newArtist)
			db.session.commit()
      # on successful db insert, flash success
			flashType = 'success'
			flash('Artist {} was successfully listed!'.format(newArtist.name)) 
		except: 
      # TODO DONE: on unsuccessful db insert, flash an error instead.
			flash('An error occurred due to database insertion error. Artist {} could not be listed.'.format(request.form['name']))
		finally:
      # Always close session
			db.session.close()
	else:
		flash(form.errors) # Flashes reason, why form is unsuccessful (not really pretty)
		flash('An error occurred due to form validation. Artist {} could not be listed.'.format(request.form['name']))

	return render_template('pages/home.html', flashType = flashType)

#	Shows
#	----------------------------------------------------------------

@app.route('/shows')
def shows():
	# displays list of shows at /shows
	# TODO: replace with real venues data.
	#       num_shows should be aggregated based on number of upcoming shows per venue.

	shows = (db.session.query(
		Venue.id.label("venue_id"), 
		Venue.name.label("venue_name"),
		Artist.id.label("artist_id"), 
		Artist.name.label("artist_name"), 
		Artist.image_link.label("artist_image_link"), 
		Show)
		.filter(Show.c.Venue_id == Venue.id)
		.filter(Show.c.Artist_id == Artist.id)
		.all())

	return render_template('pages/shows.html', shows=shows)

@app.route('/shows/create')
def create_shows():
	# renders form. do not touch.
	form = ShowForm()
	return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
	# called to create new shows in the db, upon submitting new show listing form
	# TODO: insert form data as a new Show record in the db, instead
	
	# on successful db insert, flash success
	# TODO: on unsuccessful db insert, flash an error instead.
	# e.g., flash('An error occurred. Show could not be listed.')
	# see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
	form = ShowForm(request.form)
	flash('Show was successfully listed!')
	if form.validate():
		try:
      # Create a new instance of Show with data from ShowForm
			newShow = Show.insert().values(
				Venue_id = request.form['venue_id'],
				Artist_id = request.form['artist_id'],
				start_time = request.form['start_time']
			  )
			db.session.execute(newShow) 
			db.session.commit()
			  # on successful db insert, flash success
			flashType = 'success'
			flash('Show was successfully listed!')
		except : 
      # TODO DONE: on unsuccessful db insert, flash an error instead.
			flash('An error occurred due to database insertion error. Show could not be listed.')
		finally:
      # Always close session
			db.session.close()
	else:
		flash(form.errors) # Flashes reason, why form is unsuccessful (not really pretty)
		flash('An error occurred due to form validation. Show could not be listed.')
  
	return render_template('pages/home.html', flashType = flashType)



@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
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
    app.run(debug=True)

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
