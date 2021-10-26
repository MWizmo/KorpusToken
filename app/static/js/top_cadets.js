let app = angular.module("app", []);
app.controller("ctrl", function ($scope, $http) {

    $scope.counter = 0;
    $scope.top_cadets=[];

    $scope.choose = function(cadet_id){
        let el = document.getElementById(cadet_id);
        if (el.style.border == '7px solid black'){
                el.style.border = '0';
                $scope.counter -= 1;
                for(let i=0; i<$scope.top_cadets.length; i++)
                    if ($scope.top_cadets[i]==cadet_id)
                        $scope.top_cadets.splice(i, 1);
            }
        else
            if ($scope.counter < 5){
                el.style.border = '7px solid black';
                $scope.counter += 1;
                $scope.top_cadets.push(cadet_id);
            }
    }

    $scope.confirm = function(){
        if ($scope.counter > 5){
                alert('Выберите не более 5 курсантов');
            }
        else{
            if($scope.counter < 1){
                alert('Выберите не менее 1 курсанта');
            }
            else{
                let user_data = {
                'top_cadets':$scope.top_cadets
                };
                $http({
                        method: 'POST',
                        url: '/confirm_top_cadets',
                        data: user_data,
                        async:false
                    }).then(function success (response) {
                    alert("Спасибо за ваш выбор!");
                        document.location.href = "assessment_page";
                    });
            }
        }
    }
    });