var wms_layers = [];


        var lyr_OpenStreetMap_0 = new ol.layer.Tile({
            'title': 'OpenStreetMap',
            'opacity': 1.000000,
            
            
            source: new ol.source.XYZ({
            attributions: ' ',
                url: 'https://tile.openstreetmap.org/{z}/{x}/{y}.png'
            })
        });
var format_track_1 = new ol.format.GeoJSON();
var features_track_1 = format_track_1.readFeatures(json_track_1, 
            {dataProjection: 'EPSG:4326', featureProjection: 'EPSG:3857'});
var jsonSource_track_1 = new ol.source.Vector({
    attributions: ' ',
});
jsonSource_track_1.addFeatures(features_track_1);
var lyr_track_1 = new ol.layer.Vector({
                declutter: false,
                source:jsonSource_track_1, 
                style: style_track_1,
                popuplayertitle: 'track',
                interactive: true,
                title: '<img src="styles/legend/track_1.png" /> track'
            });
var format_Fotky_2 = new ol.format.GeoJSON();
var features_Fotky_2 = format_Fotky_2.readFeatures(json_Fotky_2, 
            {dataProjection: 'EPSG:4326', featureProjection: 'EPSG:3857'});
var jsonSource_Fotky_2 = new ol.source.Vector({
    attributions: ' ',
});
jsonSource_Fotky_2.addFeatures(features_Fotky_2);
var lyr_Fotky_2 = new ol.layer.Vector({
                declutter: false,
                source:jsonSource_Fotky_2, 
                style: style_Fotky_2,
                popuplayertitle: 'Fotky',
                interactive: true,
                title: '<img src="styles/legend/Fotky_2.png" /> Fotky'
            });
var format_Fotky_podle_casu_3 = new ol.format.GeoJSON();
var features_Fotky_podle_casu_3 = format_Fotky_podle_casu_3.readFeatures(json_Fotky_podle_casu_3, 
            {dataProjection: 'EPSG:4326', featureProjection: 'EPSG:3857'});
var jsonSource_Fotky_podle_casu_3 = new ol.source.Vector({
    attributions: ' ',
});
jsonSource_Fotky_podle_casu_3.addFeatures(features_Fotky_podle_casu_3);
var lyr_Fotky_podle_casu_3 = new ol.layer.Vector({
                declutter: false,
                source:jsonSource_Fotky_podle_casu_3, 
                style: style_Fotky_podle_casu_3,
                popuplayertitle: 'Fotky_podle_casu',
                interactive: true,
                title: '<img src="styles/legend/Fotky_podle_casu_3.png" /> Fotky_podle_casu'
            });
var format_Videa_4 = new ol.format.GeoJSON();
var features_Videa_4 = format_Videa_4.readFeatures(json_Videa_4, 
            {dataProjection: 'EPSG:4326', featureProjection: 'EPSG:3857'});
var jsonSource_Videa_4 = new ol.source.Vector({
    attributions: ' ',
});
jsonSource_Videa_4.addFeatures(features_Videa_4);
var lyr_Videa_4 = new ol.layer.Vector({
                declutter: false,
                source:jsonSource_Videa_4, 
                style: style_Videa_4,
                popuplayertitle: 'Videa',
                interactive: true,
                title: '<img src="styles/legend/Videa_4.png" /> Videa'
            });

lyr_OpenStreetMap_0.setVisible(true);lyr_track_1.setVisible(true);lyr_Fotky_2.setVisible(true);lyr_Fotky_podle_casu_3.setVisible(true);lyr_Videa_4.setVisible(true);
var layersList = [lyr_OpenStreetMap_0,lyr_track_1,lyr_Fotky_2,lyr_Fotky_podle_casu_3,lyr_Videa_4];
lyr_track_1.set('fieldAliases', {'name': 'name', 'cmt': 'cmt', 'desc': 'desc', 'src': 'src', 'link1_href': 'link1_href', 'link1_text': 'link1_text', 'link1_type': 'link1_type', 'link2_href': 'link2_href', 'link2_text': 'link2_text', 'link2_type': 'link2_type', 'number': 'number', 'type': 'type', 'layer': 'layer', 'path': 'path', });
lyr_Fotky_2.set('fieldAliases', {'filename': 'filename', 'photo': 'photo', 'path': 'path', 'photo_time': 'photo_time', 'bunny_file': 'bunny_file', 'photo_url': 'photo_url', });
lyr_Fotky_podle_casu_3.set('fieldAliases', {'filename': 'filename', 'path': 'path', 'photo_time': 'photo_time', 'gpx_time': 'gpx_time', 'difference_s': 'difference_s', 'bunny_file': 'bunny_file', 'photo_url': 'photo_url', });
lyr_Videa_4.set('fieldAliases', {'filename': 'filename', 'path': 'path', 'video_time': 'video_time', 'gpx_time': 'gpx_time', 'difference_s': 'difference_s', 'bunny_file': 'bunny_file', 'video_url': 'video_url', });
lyr_track_1.set('fieldImages', {'name': '', 'cmt': '', 'desc': '', 'src': '', 'link1_href': '', 'link1_text': '', 'link1_type': '', 'link2_href': '', 'link2_text': '', 'link2_type': '', 'number': '', 'type': '', 'layer': '', 'path': '', });
lyr_Fotky_2.set('fieldImages', {'filename': '', 'photo': '', 'path': '', 'photo_time': '', 'bunny_file': '', 'photo_url': '', });
lyr_Fotky_podle_casu_3.set('fieldImages', {'filename': '', 'path': '', 'photo_time': '', 'gpx_time': '', 'difference_s': '', 'bunny_file': '', 'photo_url': '', });
lyr_Videa_4.set('fieldImages', {'filename': '', 'path': '', 'video_time': '', 'gpx_time': '', 'difference_s': '', 'bunny_file': '', 'video_url': '', });
lyr_track_1.set('fieldLabels', {'name': 'no label', 'cmt': 'no label', 'desc': 'no label', 'src': 'no label', 'link1_href': 'no label', 'link1_text': 'no label', 'link1_type': 'no label', 'link2_href': 'no label', 'link2_text': 'no label', 'link2_type': 'no label', 'number': 'no label', 'type': 'no label', 'layer': 'no label', 'path': 'no label', });
lyr_Fotky_2.set('fieldLabels', {'filename': 'no label', 'photo': 'no label', 'path': 'no label', 'photo_time': 'hidden field', 'bunny_file': 'hidden field', 'photo_url': 'hidden field', });
lyr_Fotky_podle_casu_3.set('fieldLabels', {'filename': 'no label', 'path': 'no label', 'photo_time': 'hidden field', 'gpx_time': 'hidden field', 'difference_s': 'hidden field', 'bunny_file': 'hidden field', 'photo_url': 'hidden field', });
lyr_Videa_4.set('fieldLabels', {'filename': 'no label', 'path': 'no label', 'video_time': 'hidden field', 'gpx_time': 'hidden field', 'difference_s': 'hidden field', 'bunny_file': 'hidden field', 'video_url': 'hidden field', });
lyr_Videa_4.on('precompose', function(evt) {
    evt.context.globalCompositeOperation = 'normal';
});