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

	$scope.add_status = function(sender){
	    status_id = sender.status[1];
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