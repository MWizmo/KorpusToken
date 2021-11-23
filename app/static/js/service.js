let app = angular.module("app", []);
app.controller("ctrl", function ($scope, $http) {

    $scope.res = 0;
    $scope.price = 0;
    //$scope.amount = 0;

    $scope.init = function(price){
        $scope.price = price;
    }

	$scope.change_amount = function(){
	    if($scope.amount)
	        $scope.res = $scope.amount * $scope.price;
	    else
	        $scope.res = 0;
	    if($scope.res == 0)
	        document.getElementById("button").disabled = true;
	    else
	        document.getElementById("button").disabled = false;
	}

    });