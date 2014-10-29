var edge = require('./edge'), path = require('path');
var params = {
	host: 'COM3',
	port: '12345'
};
var rfid = edge.func('rfid.csx');

rfid(params, function(err, result){
	if(err) throw err;
	console.log(result);
});

setInterval(function() {
    console.log('ok');
}, 1000);