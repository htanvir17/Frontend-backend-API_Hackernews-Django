jQuery(document).ready(function($){


         $(".votearrow").click(function(e){
              e.preventDefault()
              $.ajaxSetup({
                     beforeSend: function(xhr, settings) {
                         function getCookie(name) {
                             var cookieValue = null;
                             if (document.cookie && document.cookie != '') {
                                 var cookies = document.cookie.split(';');
                                 for (var i = 0; i < cookies.length; i++) {
                                     var cookie = jQuery.trim(cookies[i]);
                                     // Does this cookie string begin with the name we want?
                                     if (cookie.substring(0, name.length + 1) == (name + '=')) {
                                         cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                                         break;
                                     }
                                 }
                             }
                             return cookieValue;
                         }
                         if (!(/^http:.*/.test(settings.url) || /^https:.*/.test(settings.url))) {
                             // Only send the token to relative URLs i.e. locally.
                             xhr.setRequestHeader("X-CSRFToken", getCookie('csrftoken'));
                         }
                     }
                });
              var this_ = $(this)
              var likeUrl = this_.attr("likehref")
              var id = this_.attr("contid")


              if (likeUrl){
                  $.ajax({
                      url: likeUrl,
                      method: "PUT",
                      data: {},
                      success: function(data){

                        if (data.liked){
                            console.log(data)
                            $("#vote"+id).hide();
                            $("#unvotehidden"+id).show();

                            var likes = parseInt(data.points) + 1
                            $("#score"+id).text(likes + " " + 'points')

                            }



                      }, error: function(error){
                          console.log(error)
                          console.log("error")

                      }
                  })
              }
        })

         $(".unvote").click(function(e){

             e.preventDefault()
             $.ajaxSetup({
                     beforeSend: function(xhr, settings) {
                         function getCookie(name) {
                             var cookieValue = null;
                             if (document.cookie && document.cookie != '') {
                                 var cookies = document.cookie.split(';');
                                 for (var i = 0; i < cookies.length; i++) {
                                     var cookie = jQuery.trim(cookies[i]);
                                     // Does this cookie string begin with the name we want?
                                     if (cookie.substring(0, name.length + 1) == (name + '=')) {
                                         cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                                         break;
                                     }
                                 }
                             }
                             return cookieValue;
                         }
                         if (!(/^http:.*/.test(settings.url) || /^https:.*/.test(settings.url))) {
                             // Only send the token to relative URLs i.e. locally.
                             xhr.setRequestHeader("X-CSRFToken", getCookie('csrftoken'));
                         }
                     }
                });
             var this_ = $(this)
             var likeUrl = this_.attr("likehref")

             var id = this_.attr("contid")

             if (likeUrl){
                 $.ajax({
                     url: likeUrl,
                     method: "PUT",
                     data: {},
                     success: function(data){
                         console.log(data)
                         if (!data.liked){

                             $("#unvote"+id).hide();
                             $("#votehidden"+id).show();

                             if (parseInt(data.points) == 0){

                                 var points = parseInt(data.points) +1
                                 $("#score"+id).text(points + " " + 'point')

                             }

                             else {
                                 var points = parseInt(data.points) +1
                                 $("#score"+id).text(points + " " + 'point')
                             }

                         }
                     },

                     error: function(error){

                         console.log(error)
                         console.log("error")
                     }
                 })
             }
         })

         $(".votearrowhidden").click(function(e){

             e.preventDefault()
             $.ajaxSetup({
                     beforeSend: function(xhr, settings) {
                         function getCookie(name) {
                             var cookieValue = null;
                             if (document.cookie && document.cookie != '') {
                                 var cookies = document.cookie.split(';');
                                 for (var i = 0; i < cookies.length; i++) {
                                     var cookie = jQuery.trim(cookies[i]);
                                     // Does this cookie string begin with the name we want?
                                     if (cookie.substring(0, name.length + 1) == (name + '=')) {
                                         cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                                         break;
                                     }
                                 }
                             }
                             return cookieValue;
                         }
                         if (!(/^http:.*/.test(settings.url) || /^https:.*/.test(settings.url))) {
                             // Only send the token to relative URLs i.e. locally.
                             xhr.setRequestHeader("X-CSRFToken", getCookie('csrftoken'));
                         }
                     }
                });
             var this_ = $(this)
             var likeUrl = this_.attr("likehref")
             var id = this_.attr("contid")

             if (likeUrl){
                 $.ajax({
                     url: likeUrl,
                     method: "PUT",
                     data: {},
                     success: function(data){
                         console.log(data)
                         if (data.liked){
                             $("#votehidden"+id).hide();
                             $("#unvote"+id).show();
                             $("#unvotehidden"+id).show();

                              var likes = parseInt(data.points) + 1
                              $("#score"+id).text(likes + " " + 'points')


                         }
                     },

                     error: function(error){

                         console.log(error)
                         console.log("error")
                     }
                 })
             }
         })

         $(".unvotehidden").click(function(e){

             e.preventDefault()
             $.ajaxSetup({
                     beforeSend: function(xhr, settings) {
                         function getCookie(name) {
                             var cookieValue = null;
                             if (document.cookie && document.cookie != '') {
                                 var cookies = document.cookie.split(';');
                                 for (var i = 0; i < cookies.length; i++) {
                                     var cookie = jQuery.trim(cookies[i]);
                                     // Does this cookie string begin with the name we want?
                                     if (cookie.substring(0, name.length + 1) == (name + '=')) {
                                         cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                                         break;
                                     }
                                 }
                             }
                             return cookieValue;
                         }
                         if (!(/^http:.*/.test(settings.url) || /^https:.*/.test(settings.url))) {
                             // Only send the token to relative URLs i.e. locally.
                             xhr.setRequestHeader("X-CSRFToken", getCookie('csrftoken'));
                         }
                     }
                });
             var this_ = $(this)
             var likeUrl = this_.attr("likehref")
             var id = this_.attr("contid")

             if (likeUrl){
                 $.ajax({
                     url: likeUrl,
                     method: "PUT",
                     data: {},
                     success: function(data){
                         console.log(data)
                         if (!data.liked){
                             $("#unvotehidden"+id).hide();
                             $("#votehidden"+id).show();
                             $("#vote"+id).show();

                             if(parseInt(data.points) == 0){
                                 var points = parseInt(data.points) +1
                                 $("#score"+id).text(points + " " + 'point')
                             }
                             else {
                                 var points = parseInt(data.points) +1
                                 $("#score"+id).text(points + " " + 'point')
                             }

                         }
                     },

                     error: function(error){

                         console.log(error)
                         console.log("error")
                     }
                 })
             }
      })
})