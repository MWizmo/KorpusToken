let app = angular.module('app', []);

app.controller('ctrl', function ($scope, $http) {
  $scope.show_results = false;
  $scope.criterions = [];
  $scope.user_info = [];
  $scope.results = false;

  $scope.choose_voting = function () {
    if (!$scope.selected && (!$scope.startDate || !$scope.endDate)) {
      $scope.results = false;

      return;
    }

    const url = `/get_results_of_weekly_voting?${
      $scope.selected
        ? `voting_date=${$scope.selected}`
        : `start_date=${$scope.startDate}&end_date=${$scope.endDate}`
    }`;

    $http({
      method: 'GET',
      url,
      async: false,
    }).then(function success(response) {
      $scope.info = response.data['results'];
      if ($scope.info) {
        $scope.results = true;
      } else {
        $scope.results = false;
      }
      $scope.show_results = true;
    });
  };

  $scope.clear_selected = function () {
    $scope.selected = '';

    $scope.info = null;
  };

  $scope.clear_interval = function () {
    $scope.startDate = '';
    $scope.endDate = '';

    $scope.info = null;
  };
});
