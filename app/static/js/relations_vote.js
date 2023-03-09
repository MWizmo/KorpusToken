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
                $scope.results[$scope.members[i][0]] = [-1];
            }
        });
	}


    $scope.vote_for = function(member,criterion,mark){
        $scope.results[member][0]=mark;
        console.log(1);
    }

    $scope.finish_vote = function(team_id, criterion_id, is_last=0){
        //document.getElementById("finish_button").disabled = true;
        let user_data = {
            'team_id':team_id,
             'criterion_id':criterion_id,
             "results":$scope.results,
             'is_last': is_last
        };
        let flag = true;

        $scope.results.forEach(function(item, i, arr) {
            if(item[0] == -1){
                flag = false;
            }
        });

        if(flag){
            $http({
                method: 'POST',
                url: '/finish_relations_vote',
                data: user_data,
                async: false
            }).then(function success (response) {
                console.log('Анкета успешно заполнена');
                document.location.href = "start_vote";
            });
        }
        else
            alert('Оцените всех участников');

    }

});