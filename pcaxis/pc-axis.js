/**
 * Created by jonas on 21.08.17.
 */


var Px = require('px'),
    fs = require('fs');

fs.readFile(process.argv[2], 'utf8', function(err, data) {
    result = [];
    px = new Px(data);
    var keywords = px.keywords();
    px.variables().forEach(function(variable){
        result.push(px.values(variable).length)
    });
    console.log(result)
});