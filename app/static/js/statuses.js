let app = angular.module("app", []);
app.controller("ctrl", function ($scope, $http) {

    $scope.statuses = [];
    $scope.show_adding = false;

	$scope.choose_user = function(user_id){
	        $http({
                method: 'GET',
                url: '/get_statuses_of_user?user_id=' + user_id,
                async:false
            }).then(function success (response) {
                $scope.statuses = response.data['user_statuses'];
                $scope.new_statuses = response.data['new_statuses'];
                if(user_id != 0){
                    $scope.show_adding = true;
                    $scope.user_id = user_id;
                    }
                else
                    $scope.show_adding = false;

            });
	}

	$scope.func1 = function(a){
	    console.log(a.status[1]);
	}


    $scope.vote_for = function(member,criterion,mark){
            $scope.results[member][criterion-1]=mark;
            console.log($scope.results);
        }

        $scope.finish_vote = function(team_id,axis_id){
            let user_data = {
                'team_id':team_id,
                 'axis':axis_id,
                 "results":$scope.results
            };
            console.log(user_data);
            $http({
                method: 'POST',
                url: '/finish_vote',
                data: user_data,
                async: false
            }).then(function success (response) {
                document.location.href = "assessment";
            });

        }

    });