// Code goes here
(() => {
  angular
  .module('dateRangeDemo', ['ui.bootstrap', 'rzModule'])
  .controller('dateRangeCtrl', function dateRangeCtrl($scope, $http) {
    var vm = this;

    // Single Date Slider    
    var dates = [];
    for (var i = 1; i <= 31; i++) {
      dates.push(new Date(2016, 7, i));
    }
    $scope.slider_dates = {
      value: new Date(2016, 7, 15),
      options: {
        stepsArray: dates,
        translate: function(date) {
          if (date !== null)
            return date.toDateString();
          return '';
        }
      }
    };
    
    // Date Range Slider
    var floorDate = new Date(2015, 0, 1).getTime();
    var ceilDate = new Date(2015, 0, 31).getTime();
    var minDate = new Date(2015, 0, 11).getTime();
    var maxDate = new Date(2015, 0, 20).getTime();
    var millisInDay = 24*60*60*1000;
      

    var monthNames =
    [
      "JAN", "FEB", "MAR", "APR", "MAY", "JUN", "JUL", "AUG", "SEP", "OCT", "NOV", "DEC"
    ];

    var formatDate = function (date_millis)
    {
      var date = new Date(date_millis);
      var month = date.getMonth() + 1; // Because JavaScript months start from 0
      var day = date.getDate();
      var year = date.getFullYear();

      // We want to return a date string in format 'yyyy-mm-dd'
      return `${year}-${month < 10 ? "0" + month : month}-${day < 10 ? "0" + day : day}`;
    }

    //Range slider config 
    $scope.dateRangeSlider = {
      minValue: minDate,
      maxValue: maxDate,
      options: {
        floor: floorDate,
        ceil: ceilDate,
        step: millisInDay,
        showTicks: false,
        draggableRange: true,
        translate: function(date_millis) {
          if ((date_millis !== null)) {
            var dateFromMillis = new Date(date_millis);
            return formatDate(dateFromMillis);
          }
          return '';
        },
        onChange: function() {
            $http.post('http://localhost:5000/filter_by_date', {
                min_date: formatDate($scope.dateRangeSlider.minValue),
                max_date: formatDate($scope.dateRangeSlider.maxValue)
            }).then(function(response) {
                let data = response.data;
                let tableBody = document.getElementById("dataTable").querySelector("tbody");
                tableBody.innerHTML = "";  // Clear current table rows
                
                data.forEach(row => {
                    let tr = document.createElement("tr");
                    // Adjust the below line based on your dataframe columns
                    tr.innerHTML = `<td>${row.column_name1}</td><td>${row.column_name2}</td>...`; 
                    tableBody.appendChild(tr);
                });
            });
        }
      }
    };
    
  });
})();

// (() => {
//   angular
//   .module('dateRangeDemo', ['ui.bootstrap', 'rzModule'])
//   .controller('dateRangeCtrl', function dateRangeCtrl($scope) {
//     var vm = this;

//     // Single Date Slider    
//     var dates = [];
//     for (var i = 1; i <= 31; i++) {
//       dates.push(new Date(2016, 7, i));
//     }
//     $scope.slider_dates = {
//       value: new Date(2016, 7, 15),
//       options: {
//         stepsArray: dates,
//         translate: function(date) {
//           if (date !== null)
//             return date.toDateString();
//           return '';
//         }
//       }
//     };
    
//     // Date Range Slider
//     var floorDate = new Date(2015, 0, 1).getTime();
//     var ceilDate = new Date(2015, 0, 31).getTime();
//     var minDate = new Date(2015, 0, 11).getTime();
//     var maxDate = new Date(2015, 0, 20).getTime();
//     var millisInDay = 24*60*60*1000;
      


//     var monthNames =
//     [
//       "JAN", "FEB", "MAR", "APR", "MAY", "JUN", "JUL", "AUG", "SEP", "OCT", "NOV", "DEC"
//     ];

//     var formatDate = function (date_millis)
//     {
//       var date = new Date(date_millis);
//       return date.getDate()+"-"+monthNames[date.getMonth()]+"-"+date.getFullYear();
//     }


//     //Range slider config 
//     $scope.dateRangeSlider = {
//       minValue: minDate,
//       maxValue: maxDate,
//       options: {
//         floor: floorDate,
//         ceil: ceilDate,
//         step: millisInDay,
//         showTicks: false,
//         draggableRange: true,
//         translate: function(date_millis) {
//           if ((date_millis !== null)) {
//             var dateFromMillis = new Date(date_millis);
//             // console.log("date_millis="+date_millis);
//             // return dateFromMillis.toDateString();
//             return formatDate(dateFromMillis);
//           }
//           return '';
//         }
//       }
//     };
    
//   });
// })();



