let app = angular.module("app", []);
app.controller("ctrl", function ($scope, $http) {

    $scope.show_results = false;
    $scope.criterions = [];
    $scope.user_info = [];
    $scope.results = false;

	$scope.choose_voting = function(){
	        console.log(1);
	        voting_id = $scope.selected;
	        $http({
                method: 'GET',
                url: '/get_results_of_weekly_voting?voting_date=' + voting_id,
                async:false
            }).then(function success (response) {
                $scope.info = response.data['results'];
                if($scope.info){
                    $scope.results = true;
                    }
                else{
                    $scope.results = false;
                }
                $scope.show_results = true;
            });
	}
    });