let app = angular.module("app", []);
app.controller("ctrl", function ($scope, $http) {

	$scope.results = [];

	$scope.start_voting = function(team_id, my_answers){
        $http({
            method: 'GET',
            url: '/get_members_of_team?team_id=' + team_id,
            async:false
        }).then(function success (response) {
            $scope.members = response.data['members'];
            $scope.results = [];
            for(let i=0;i<my_answers.length;i++){
               $scope.results[$scope.members[i][0]] = [my_answers[i]];
            }
        });

	}

	$scope.check = function(member,criterion){
        if($scope.results[member]){
            if($scope.results[member][0]==1)
                return 1;
            else
                return 0;
        }
    }


    $scope.vote_for = function(member,criterion,mark){
        $scope.results[member][0]=mark;
    }

    $scope.finish_vote = function(team_id, axis_id, criterion_id, is_last=0){
        //document.getElementById("finish_button").disabled = true;
        let user_data = {
            'team_id':team_id,
             'axis':axis_id,
             'criterion_id':criterion_id,
             "results":$scope.results,
             'is_last': is_last,
             'revote': 1
        };
        let flag = true;
        if(flag){
            $http({
                method: 'POST',
                url: '/finish_vote',
                data: user_data,
                async: false
            }).then(function success (response) {
                console.log('Анкета успешно заполнена');
                document.location.href = response.data.url;
            });
        }
        else
            alert('Оцените всех участников');

    }

});