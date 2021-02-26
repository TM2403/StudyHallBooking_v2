$(function() {
    getSeatMap();
    setInterval(getSeatMap, 5000);

    var tippies = new Array(54)

    function getSeatMap(){
        $.ajax({
          url: '{% url "getseatmap" %}',
          dataType: 'json',
          }).done(function(data,textStatus,jqXHR) {
            updateSeatMap(data);
           // $("#test1").text(data[0]["fields"]);
            //console.log(data);

            }).fail(function(jqXHR, textStatus, errorThrown ) {

            }).always(function(){
            
            });
    }
    
    function updateSeatMap(data){
        $.each(data, function(index, seat){
            seat_id = seat["seat_id"];
            full_name = seat["full_name"];
            full_class = seat["full_hr_class"];
            student_id = seat["student_id"];
            status = seat["status"];
            internet = seat["internet"];

            updateTippy(status, seat_id, full_name, full_class, student_id, internet);

            $("#seat" + seat_id.toString()).removeAttr("class");
            switch(seat["status"]){
                case 0:
                    $("#seat" + seat_id.toString()).addClass("bg-success");
                break;
                case 1:
                    $("#seat" + seat_id).addClass("bg-danger taken");
                    
                break;
                case 2:
                    $("#seat" + seat_id).addClass("bg-warning taken");
                break;
                case 9:
                    $("#seat" + seat_id).addClass("bg-secondary unavailable");
                break;
            }
        })
    }


    function updateTippy(current_status, seat_id, full_name, full_class, student_id, internet){

        switch(current_status){
            case "0":
            case "9":
                if(tippies[seat_id - 1] != null)　tippies[seat_id - 1].destroy();
                break;

            case "1":
            case "2":
                if(tippies[seat_id - 1] != null){
                    tippies[seat_id - 1].setContent(getToolTipsContent(full_name, full_class, student_id, internet));
                }else{
                    tippies[seat_id - 1] = new tippy(document.querySelector("#seat" + seat_id.toString()), {
                                    content: getToolTipsContent(full_name, full_class, student_id, internet),
                                    allowHTML: true,
                                    theme: 'light-border',
                                });
                }
                break;
        }
    }

    function getToolTipsContent(full_name, full_class, student_id, internet){
        if(internet == true)
            internet_display = '有';
        else
            internet_display = '無';
        
        html = '<span class="seatmap-tooltip">' + full_name 
            + '<br/>' + full_class 
            + '<br/>' + student_id 
            + '<br/>インターネット:' + internet_display + '</span>';

        return html;
    }

  });

