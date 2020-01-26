let app = angular.module("app", []);
app.controller("ctrl", function ($scope, $http) {

	$scope.results = [];

	$scope.start_voting = function(team_id){
	        $http({
                method: 'GET',
                url: '/get_members_of_team?team_id=' + team_id,
                async:false
            }).then(function success (response) {
                $scope.members = response.data['members'];
                $scope.results = [];
                for(let i=0;i<$scope.members.length;i++){
                    $scope.results[$scope.members[i][0]] = [0,0,0,0,0,0,0,0,0];
                }
                console.log($scope.results);
            });
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
                console.log(1214);
            });

        }

    });