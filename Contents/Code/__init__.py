ART = 'bbcradio-art.jpg'
ICON = 'bbcradio-icon.png'

URL = "http://www.bbc.co.uk/radio/services"

REGEX_PLAYLIST_PLS = Regex('File1=(https?://.+)')
MP3_URL = String.Decode('aHR0cDovL29wZW4ubGl2ZS5iYmMuY28udWsvbWVkaWFzZWxlY3Rvci81L3NlbGVjdC9tZWRpYXNldC9odHRwLWljeS1tcDMtYS92cGlkLyVzL2Zvcm1hdC9wbHMucGxz')
HLS_URL = String.Decode('aHR0cDovL29wZW4ubGl2ZS5iYmMuY28udWsvbWVkaWFzZWxlY3Rvci81L3NlbGVjdC92ZXJzaW9uLzIuMC9mb3JtYXQvanNvbi9tZWRpYXNldC9hcHBsZS1pcGFkLWhscy92cGlkLyVz')

FEEDID = {
	'radio1':			'bbc_radio_one',
	'1xtra':			'bbc_1xtra',
	'radio2':			'bbc_radio_two',
	'radio3':			'bbc_radio_three',
	'radio4':			'bbc_radio_fourfm',
	'radio4extra':		'bbc_radio_four_extra',
	'radio5live':		'bbc_radio_five_live',
	'5livesportsextra':	'bbc_radio_five_live_sports_extra',
	'6music':			'bbc_6music',
	'asiannetwork':		'bbc_asian_network'
}

####################################################################################################
def Start():
	ObjectContainer.art = R(ART)
	ObjectContainer.title1 = F('title')
	TrackObject.thumb = R(ICON)

####################################################################################################     
@handler('/music/bbcradio', 'BBC Radio', thumb=ICON, art=ART)
def MainMenu():
	
	oc = ObjectContainer()

	pageElement = HTML.ElementFromURL( URL)
	
	for item in pageElement.xpath("//span[@class='plp-stations-content-rich']"): 
		try:
			section = item.xpath("./a[@class='cf']")[0]
			radioID = section.xpath("./@href")[0][1:]

			radioName = section.xpath("./div")[2].xpath("./div")[0].xpath("./span")[1].text
			onNow = section.xpath("./div")[2].xpath("./div")[0].xpath("./h3")[0].text
			showtitle = "BBC " + radioName + " | " + onNow
			radioTime = section.xpath("./div")[2].xpath("./div")[0].xpath("./span")[0].text
			summary = radioTime + onNow

			img = R("bbcradio-"+ radioID +".png")
			if Prefs["USE_SHOW_ARTWORK"]:
				img = section.xpath("./div")[0].xpath("./img")[0].xpath("./@src")[0]

			image = str(img)
			oc.add(CreateTrackObject(url=radioID, title=showtitle, thumb=image, summary=summary))
			oc.art=image
		except Exception, e:
			Log(e)
			pass

	return oc


	####################################################################################################
def CreateTrackObject(url, title, thumb, summary, include_container=False):

	content = HTTP.Request(MP3_URL % FEEDID[url], cacheTime=0).content
	file_url = REGEX_PLAYLIST_PLS.search(content)
	feedURL = file_url.group(1)
	Log( feedURL)

	if url.endswith('.m3u8'):
		container = Container.MP3
		audio_codec = AudioCodec.AAC
	else:
		container = Container.MP3
		audio_codec = AudioCodec.MP3

	track_object = TrackObject(
		key = Callback(CreateTrackObject, url=feedURL, title=title, thumb=thumb, summary=summary),
		rating_key = feedURL,
		title = title,
		thumb=thumb,
		summary = summary,
		items = [
			MediaObject(
				parts = [
					PartObject(key=feedURL)
				],
				container = container,
				audio_codec = audio_codec,
				audio_channels = 2
			)
		]
	)

	if include_container:
		return ObjectContainer(objects=[track_object])
	else:
		return track_object
