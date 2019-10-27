function getCookie(name) {
            var cookieValue = null;
            if (document.cookie && document.cookie !== '') {
                var cookies = document.cookie.split(';');
                for (var i = 0; i < cookies.length; i++) {
                    var cookie = jQuery.trim(cookies[i]);
                    // Does this cookie string begin with the name we want?
                    if (cookie.substring(0, name.length + 1) === (name + '=')) {
                        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                        break;
                    }
                }
            }
            return cookieValue;
        }


                          if ( !$("#customizations").val()) {
                              $("#amount").hide();
                          }
                          function get_amount(){

                    var csrftoken = getCookie('csrftoken');
                    var customizations = document.getElementById('customizations').value;


                    var currency = $("#myform input[type='radio']:checked").val();

                    var user_id = "{{ user.id }}";
                    $('#inpnumber').val(customizations);
                    $('#inpcurrecny').val(currency);


                    if ( !$("#customizations").val()) {

                          }
                    else {
                        $.ajax({
                            url: '/service/amount-sop/',
                            type: 'post',
                            data: {
                                'customizations': customizations,
                                'currency': currency,
                                'csrfmiddlewaretoken': csrftoken,
                                'user_id': user_id,
                            },

                            success: function (data) {
                                var x = data.price;
                                var y = x / 100;
                                // {#alert(y);#}
                                $('#price').text(data.price_d + y);
                                $("#amount").show();
                                if (!$("#customizations").val()) {
                                    $("#amount").hide();


                                }
                                $("#rzp-button1").prop("disabled", false);
                                // {#alert(data.curr);#}
                                options.amount = data.price;
                                options.currency = data.curr;
                                options.description = data.raztext;
                                $('#inpamount').val(data.price);


                                var rzp1 = new Razorpay(options);

                                document.getElementById('rzp-button1').onclick = function (e) {
                                    rzp1.open();


                                };

                            },

                            failure: function (data) {
                            }
                        });
                    }

                }





         if ( !$("#num_lor").val()) {
                              $("#amount").hide();
                          }

        function get_lor_amount(){

                var user_id = "{{ user.id }}";
                var csrftoken = getCookie('csrftoken');
                var numLor = document.getElementById('num_lor').value;
                var currency = $("#myform input[type='radio']:checked").val();
                var user_id = "{{ user.id }}";
                $('#inpnumber').val(numLor);
                 $('#inpcurrecny').val(currency);


                 if ( !$("#num_lor").val()) {

                          }
                    else {

                $.ajax({
                        url: '/service/amount-lor/',
                        type: 'post',
                        data: {
                            'numLor': numLor,
                            'csrfmiddlewaretoken': csrftoken,
                            'currency' : currency,
                            'user_id': user_id,
                        },

                        success: function (data) {

                                var x = data.price;
                                var y = x/100;
                                // {#alert(y);#}
                                $('#price').text(data.price_d + y);



                            $("#amount").show();


                                if ( !$("#num_lor").val()) {
                              $("#amount").hide();
                            }

                                $("#rzp-button1").prop("disabled",false);
                                    // {#alert(data.curr);#}
                                    options.amount = data.price;
                                    options.currency =data.curr;
                                    options.description = data.raztext;
                                    $('#inpamount').val(data.price);

                                    var rzp1 = new Razorpay(options);

                                    document.getElementById('rzp-button1').onclick = function(e){
                                        rzp1.open();

                                    };



                            },

                        failure: function (data) {
                        }
                    });


            }}



                              $("#amount").hide();



                        function get_univ_short_amount(){




                                var topic = document.getElementById('topic').textContent;
                                var csrftoken = getCookie('csrftoken');
                                var user_id = "{{ user.id }}";

                                var currency = $("#myform input[type='radio']:checked").val();
                                 $('#inpcurrecny').val(currency);




                                $.ajax({
                                        url: '/service/univ-shortlist/',
                                        type: 'post',
                                        data: {
                                            'currency': currency,
                                            'csrfmiddlewaretoken': csrftoken,
                                            'user_id': user_id,
                                            'topic': topic,
                                        },

                                        success: function (data) {

                                                var x = data.price;
                                                var y = x/100;

                                                $('#price').text(data.price_d + y);
                                                $("#amount").show();
                                                $("#rzp-button1").prop("disabled",false);


                                        $("#choose").hide();

                                    options.amount = data.price;
                                    options.currency =data.curr;
                                    options.description = data.raztext;
                                    $('#inpamount').val(data.price);

                                    var rzp1 = new Razorpay(options);

                                    document.getElementById('rzp-button1').onclick = function(e){
                                        rzp1.open();

                                    };




                                            },

                                        failure: function (data) {
                                        }
                                    });


                            }






                              $("#amount").hide();

                        function gre_amount(){


                                var topic = document.getElementById('topic').textContent;
                                var csrftoken = getCookie('csrftoken');
                                var user_id = "{{ user.id }}";
                                var currency = $("#myform input[type='radio']:checked").val();
                                $('#inpcurrecny').val(currency);



                                $.ajax({
                                        url: '/service/gre-consult/',
                                        type: 'post',
                                        data: {
                                            'currency': currency,
                                            'csrfmiddlewaretoken': csrftoken,
                                            'user_id': user_id,
                                            'topic': topic,
                                        },

                                        success: function (data) {

                                                var x = data.price;
                                                var y = x/100;
                                                // {#alert(y);#}
                                                $('#price').text(data.price_d + y);
                                                $("#amount").show();
                                                $("#rzp-button1").prop("disabled",false);


                                        $("#choose").hide();

                                    options.amount = data.price;
                                    options.currency =data.curr;
                                    options.description = data.raztext;
                                    $('#inpamount').val(data.price);

                                    var rzp1 = new Razorpay(options);

                                    document.getElementById('rzp-button1').onclick = function(e){
                                        rzp1.open();

                                    };



                                            },

                                        failure: function (data) {
                                        }
                                    });


                            }


                              $("#amount").hide();




                        function toefl_amount(){

                                var topic = document.getElementById('topic').textContent;
                                var csrftoken = getCookie('csrftoken');
                                var currency = $("#myform input[type='radio']:checked").val();
                                var user_id = "{{ user.id }}";
                                $('#inpcurrecny').val(currency);



                                $.ajax({
                                        url: '/service/toefl-consult/',
                                        type: 'post',
                                        data: {
                                            'currency': currency,
                                            'csrfmiddlewaretoken': csrftoken,
                                            'user_id': user_id,
                                            'topic': topic,
                                        },

                                        success: function (data) {


                                                 var x = data.price;
                                                var y = x/100;
                                                // {#alert(y);#}
                                                $('#price').text(data.price_d + y);
                                                $("#amount").show();
                                                $("#rzp-button1").prop("disabled",false);


                                        $("#choose").hide();

                                    options.amount = data.price;
                                    options.currency =data.curr;
                                    options.description = data.raztext;
                                    $('#inpamount').val(data.price);

                                    var rzp1 = new Razorpay(options);

                                    document.getElementById('rzp-button1').onclick = function(e){
                                        rzp1.open();
                                    };

                                            },

                                        failure: function (data) {
                                        }
                                    });


                            }

                        $("#amount").hide();


                        function history_amount(){


                                var topic = document.getElementById('topic').textContent;
                                var csrftoken = getCookie('csrftoken');
                                var currency = $("#myform input[type='radio']:checked").val();
                                var user_id = "{{ user.id }}";
                                $('#inpcurrecny').val(currency);




                                $.ajax({
                                        url: '/service/history-draft/',
                                        type: 'post',
                                        data: {
                                            'currency': currency,
                                            'csrfmiddlewaretoken': csrftoken,
                                            'user_id': user_id,
                                            'topic': topic,
                                        },

                                        success: function (data) {


                                               var x = data.price;
                                                var y = x/100;
                                                // {#alert(y);#}
                                                $('#price').text(data.price_d + y);
                                                $("#amount").show();
                                                $("#rzp-button1").prop("disabled",false);


                                        $("#choose").hide();

                                    options.amount = data.price;
                                    options.currency =data.curr;
                                    options.description = data.raztext;
                                    $('#inpamount').val(data.price);

                                    var rzp1 = new Razorpay(options);

                                    document.getElementById('rzp-button1').onclick = function(e){
                                        rzp1.open();

                                    };
                                            },

                                        failure: function (data) {
                                        }
                                    });


                            }



                             $("#amount").hide();
                        function com_application(){


                                var topic = document.getElementById('topic').textContent;
                                var csrftoken = getCookie('csrftoken');
                                var currency = $("#myform input[type='radio']:checked").val();
                                var user_id = "{{ user.id }}";
                                $('#inpcurrecny').val(currency);





                                $.ajax({
                                        url: '/service/complete-application/',
                                        type: 'post',
                                        data: {
                                            'currency': currency,
                                            'csrfmiddlewaretoken': csrftoken,
                                            'user_id': user_id,
                                            'topic': topic,
                                        },

                                        success: function (data) {


                                            var x = data.price;
                                                var y = x/100;
                                                // {#alert(y);#}
                                                $('#price').text(data.price_d + y);
                                                $("#amount").show();
                                                $("#rzp-button1").prop("disabled",false);


                                        $("#choose").hide();

                                    options.amount = data.price;
                                    options.currency =data.curr;
                                    options.description = data.raztext;
                                    $('#inpamount').val(data.price);

                                    var rzp1 = new Razorpay(options);

                                    document.getElementById('rzp-button1').onclick = function(e){
                                        rzp1.open();

                                    };
                                            },

                                        failure: function (data) {
                                        }
                                    });


                            }


                             $("#amount").hide();
                        function admission_plan(){


                                var topic = document.getElementById('topic').textContent;
                                var csrftoken = getCookie('csrftoken');
                                var currency = $("#myform input[type='radio']:checked").val();
                                var user_id = "{{ user.id }}";
                                $('#inpcurrecny').val(currency);

                                $.ajax({
                                        url: '/service/create-admission-plan/',
                                        type: 'post',
                                        data: {
                                            'currency': currency,
                                            'csrfmiddlewaretoken': csrftoken,
                                            'user_id': user_id,
                                            'topic': topic,
                                        },

                                        success: function (data) {


                                            var x = data.price;
                                                var y = x/100;
                                                // {#alert(y);#}
                                                $('#price').text(data.price_d + y);
                                                $("#amount").show();
                                                $("#rzp-button1").prop("disabled",false);


                                        $("#choose").hide();

                                    options.amount = data.price;
                                    options.currency =data.curr;
                                    options.description = data.raztext;
                                    $('#inpamount').val(data.price);

                                    var rzp1 = new Razorpay(options);

                                    document.getElementById('rzp-button1').onclick = function(e){
                                        rzp1.open();

                                    };



                                            },

                                        failure: function (data) {
                                        }
                                    });


                            }


                             $("#amount").hide();

                        function resume_amount(){

                                var topic = document.getElementById('topic').textContent;


                                var user_id = "{{ user.id }}";


                                var csrftoken = getCookie('csrftoken');
                                var currency = $("#myform input[type='radio']:checked").val();
                                $('#inpcurrecny').val(currency);

                                $.ajax({
                                        url: '/service/help-resume/',
                                        type: 'post',
                                        data: {
                                            'currency': currency,
                                            'csrfmiddlewaretoken': csrftoken,
                                            'user_id': user_id,
                                            'topic': topic,
                                        },

                                        success: function (data) {


                                            var x = data.price;
                                                var y = x/100;

                                                $('#price').text(data.price_d + y);
                                                $("#amount").show();
                                                $("#rzp-button1").prop("disabled",false);


                                        $("#choose").hide();

                                    options.amount = data.price;
                                    options.currency =data.curr;
                                    options.description = data.raztext;
                                    $('#inpamount').val(data.price);

                                    var rzp1 = new Razorpay(options);

                                    document.getElementById('rzp-button1').onclick = function(e){
                                        rzp1.open();

                                    };


                                            },

                                        failure: function (data) {
                                        }
                                    });
                            }

