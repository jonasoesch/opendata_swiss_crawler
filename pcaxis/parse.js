var Px = require('px'),
    fs = require('fs');
	
fs.readFile('px-x-1503030000_203.px', 'utf8', function(err, data) {
	px = new Px(data);
    console.log(px.entries())
});
