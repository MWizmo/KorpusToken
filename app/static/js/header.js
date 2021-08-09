$(document).ready(function() {


});
function reduce_block (polygon_id){
    move('#block' + polygon_id)
      .scale(1)
      .end();
    }

function enlarge_block(polygon_id, text=""){
    move('#block' + polygon_id)
      .scale(1.05)
      .end();
   }