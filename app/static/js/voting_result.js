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
                url: '/get_results_of_voting?voting_id=' + voting_id,
                async:false
            }).then(function success (response) {
                $scope.criterions = response.data['criterions'];
                info = response.data['user_info'];
                if($scope.criterions){
                    $scope.results = true;
                    $scope.user_info = [];
                    for(let i=0; i<info.length; ++i){
                        let row = info[i];
                        let new_row = [];
                        for(let j=0; j<row.length; ++j){
                            new_row.push({
                                key:   j,
                                value: row[j]
                            });
                        }
                        $scope.user_info.push(new_row);
                    }
                    }
                else{
                    $scope.results = false;
                }
                $scope.show_results = true;
            });
	}

	$scope.add_status = function(){
	    status_id = $scope.status_selected;
	    if(status_id == 4){
            $http({
                    method: 'GET',
                    url: '/get_teams_of_user?user_id=' + user_id,
                    async:false
                }).then(function success (response) {
                    $scope.teams = response.data['teams'];
                    $scope.show_teams = true;
                });
	    }
	    else{
	        let user_data = {
                'user_id':$scope.user_id,
                'status_id':status_id
            };
            $http({
                    method: 'POST',
                    url: '/add_status',
                    data: user_data,
                    async:false
                }).then(function success (response) {
                    $scope.choose_user($scope.user_id);
                });
        }
	}

	$scope.add_teamlead = function(){
	    team_id = $scope.team_selected;
        let user_data = {
            'user_id':$scope.user_id,
            'team_id':team_id
        };
        $http({
                method: 'POST',
                url: '/add_teamlead',
                data: user_data,
                async:false
            }).then(function success (response) {
                $scope.show_teams = false;
                $scope.choose_user($scope.user_id);
            });

	}

	$scope.delete_status = function(sender){
	    status_id = sender.status[1];
	    let user_data = {
                'user_id':$scope.user_id,
                'status_id':status_id
            };
	    $http({
                method: 'POST',
                url: '/delete_status',
                data: user_data,
                async:false
            }).then(function success (response) {
                $scope.choose_user($scope.user_id);
            });
	}

    });