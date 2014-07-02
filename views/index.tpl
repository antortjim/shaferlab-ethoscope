<!DOCTYPE>
<html  >
<!--[if lt IE 7]>      <html class="no-js lt-ie9 lt-ie8 lt-ie7"> <![endif]-->
<!--[if IE 7]>         <html class="no-js lt-ie9 lt-ie8"> <![endif]-->
<!--[if IE 8]>         <html class="no-js lt-ie9"> <![endif]-->
<!--[if gt IE 8]><!--> <html class="no-js"> <!--<![endif]-->
    <head>
        <meta charset="utf-8">
        <meta http-equiv="X-UA-Compatible" content="IE=edge,chrome=1">
        <title></title>
        <meta name="description" content="">
        <meta name="viewport" content="width=device-width, initial-scale=1">

        <link rel="stylesheet" href="static/css/bootstrap.min.css">
        <style>
            body {
                padding-top: 50px;
                padding-bottom: 20px;
            }
        </style>
        <link rel="stylesheet" href="static/css/bootstrap-theme.min.css">
        <link rel="stylesheet" href="static/css/main.css">

        <script src="static/js/vendor/modernizr-2.6.2-respond-1.1.0.min.js"></script>
                <script type="text/javascript" src="static/js/vendor/angular.min.js"></script>
        <script type="text/javascript"  src="static/js/main.js"></script>
        
    </head>
    <body ng-app="fly">
        <!--[if lt IE 7]>
            <p class="browsehappy">You are using an <strong>outdated</strong> browser. Please <a href="http://browsehappy.com/">upgrade your browser</a> to improve your experience.</p>
        <![endif]-->
    <div class="navbar navbar-inverse navbar-fixed-top" role="navigation">
      <div class="container" ng-controller="changeMachineIdCtrl">
        <div class="navbar-header">
          <button type="button" class="navbar-toggle" data-toggle="collapse" data-target=".navbar-collapse">
            <span class="sr-only">Toggle navigation</span>
            <span class="icon-bar"></span>
            <span class="icon-bar"></span>
            <span class="icon-bar"></span>
          </button>
          <a id="machineid" class="navbar-brand" href="/"  ng-click="changeMachineId()">PySolo ControlPanel: {{machineId}}</a>
            
        </div>
        <div class="navbar-collapse collapse">
          <form class="navbar-form navbar-right" role="form">
            <div class="form-group">
              <input type="text" placeholder="Email" class="form-control">
            </div>
            <div class="form-group">
              <input type="password" placeholder="Password" class="form-control">
            </div>
            <button type="submit" class="btn btn-success">Sign in</button>
          </form>
        </div><!--/.navbar-collapse -->
      </div>
    </div>

    <!-- Main jumbotron for a primary marketing message or call to action -->
    <div class="jumbotron">
      <div class="container text-center">
        <div class="row">
        <h2>PySolo-Video Browser editor</h2>
          <div id="ROI-input" class="col-md-12">
            <canvas id="ROIView" width="500" height="300"></canvas>
              <!--<canvas id="drawingCanvas" width="500" height="300"></canvas>-->
         </div>
          </div>
          <div class="row ">
                <div class=" col-md-12">
                    <div class="btn-group">
                        <button type="button" id="removeLast" class="btn btn-default" href="#" role="button">Remove last</button>
                        <button type="button" id="autoMask"class="btn btn-default" href="#" role="button">Auto mask</button>
                        </div>
                    <div class="btn-group">
                        <button type="button" id="saveRoi" class="btn btn-default" href="#" role="button">Save</button>
                        <button type="button" id="loadRoi"class="btn btn-default" href="#" role="button">Load</button>
                    </div>
                </div>
            
            <div class="row text-center">
                <div id="pickloaded" class="col-md-12">
                    
                </div>
            </div>
       </div>
      </div>
    </div>

    <div class="container">
      <!-- Example row of columns -->
      <div class="row">
        <div class="col-md-4">
          <h2>Refresh</h2>
          <p>Click Here to refresh the camera image</p>
          <p><button type="button" id="refreshBackground"class="btn btn-default" href="#" role="button">Refresh</button></p>
        </div>
%if status == True:
          <div class="col-md-4">
            <h2>Tracking ongoing</h2>
            <p>Tracking is already ongoing</p>
              <p><button type="button" id="start" class=" btn btn-success" href="#" role="button" disabled>Start</button></p>
         </div>
        <div class="col-md-4">
          <h2>Stop Tracking</h2>
          <p>Stops the tracking system.</p>
          <p><button type="button" id="stop" class="btn btn-danger" href="#" role="button">Stop</button></p>
        </div>
%else:
        <div class="col-md-4">
          <h2>Start Tracking</h2>
          <p>Select tracking type</p>
             <form class="">
              <div class="track-select">
                <div class="input-group"><label>
                    <input type="radio" name="optionTrack" id="optionTrack0" value="0">
                    Position</label>
                    
                </div>
                <div class="input-group ">
                    <input type="radio" name="optionTrack" id="optionTrack1" value="1">
                    <label>Distance</label>
                </div>
                <div class="input-group">
                    <input type="radio" name="optionTrack" id="optionTrack2" value="2">
                    <label>XY Coordinates</label>
                </div>
              </div>
            <p><button type="submit" id="start" class=" btn btn-success" href="#" role="button" >Start</button></p>
              </form>
        </div>
        <div class="col-md-4">
              <h2>Stop Tracking</h2>
              <p>Stops the tracking system.</p>
              <p><button type="button" id="stop" class="btn btn-danger" href="#" role="button" disabled>Stop</button></p>
         </div>
%end
       </div>
      <hr>       
      <div class="row status"  ng-controller="flyDataCtrl as flyData">
      <h3>Last collected data:</h3>
      <table class="table table-resposive table-striped small">
      <tr>
        <th>id</th>
        <th>date</th>
        <th>time</th>
        <th>active?</th>
        <th>fps</th>
        <th>trackType</th>
        <th>SD</th>
        <th>N/A</th>
        <th>N/A</th>
        <th>light</th>
      </tr>
      <tr>
            <td ng-repeat="n in [0,1,2,3,4,5,6,7,8,9]">
                {!flyData.data[n]!}
            </td>
        </tr>
        <tr>
            <th ng-repeat="n in [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16]">
            {!n!}
            </th>
        </tr>
        <tr>
            <td ng-repeat="n in [10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25]">
                {!flyData.data[n]!}
            </td>
        </tr>
        <tr>
            <th ng-repeat="n in [17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32]">
            {!n!}
            </th>
        </tr>
         <tr>
            <td ng-repeat="n in [26,27,28,29,30,31,32,33,34,35,36,37,38,39,40,41,42]">
                {!flyData.data[n]!}
            </td>
        </tr>
      </table>



      <hr>
     <h4>Disk space used:</h4>
      <div class="progress">
         <div class="progress-bar" role="progressbar" aria-valuenow="{{freeSpace}}" aria-valuemin="0" aria-valuemax="100" style="width: {{freeSpace}};">
            <span class="">{{freeSpace}}</span>
        </div>
       </div>

      <div class="download col-md-2">
        <a  class="btn btn-warning" href="/downloadData/{{machineId}}" download>Dowload Data</a>
      </div>
      <div class="delete col-md-offset-4 col-md-4" ng-controller="deleteDataCtrl">
        <button  class="btn btn-danger"  ng-click="deleteData()">Delete Data</button>
      </div>
   </div>
      <hr>
      
      <footer>
        <p>&copy; Polygonal Tree 2014</p>
      </footer>
    </div> <!-- /container -->        
        <script src="static/js/vendor/jquery-1.11.0.min.js"></script>

        <script src="static/js/vendor/bootstrap.min.js"></script>

    </body>
</html>

