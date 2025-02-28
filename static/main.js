window.filterDataOnDate = function(){};
window.restoreRealTime = function(){};
$(document).ready(function () {
    const ctx = document.getElementById("myTempChart").getContext("2d");
    const Tctx = document.getElementById("myHumChart").getContext("2d");
    
    //criação dos elementos gráficos
    const myTempChart = new Chart(ctx, {
      type: "line",
      data: {
        datasets: [{ label: "Temperature",  }],
      },
      options: {
        borderWidth: 3,
        borderColor: ['rgba(255, 99, 132, 1)',],
      },
    });
    const myHumChart = new Chart(Tctx, {
      type: "line",
      data: {
        datasets: [{ label: "Humidity",  }],
      },
      options: {
        borderWidth: 3,
        borderColor: ['rgba(0, 177, 228, 1)',],
      },
    });   
    //função que adiciona dados de temperatura
    function tempAddData(label, data) {
      myTempChart.data.labels.push(label);
      myTempChart.data.datasets.forEach((dataset) => {
        dataset.data.push(data);
      });
      myTempChart.update();
    }
    //função que remove a primeira leitura quando limite é atingido
    function tempRemoveFirstData() {
      myTempChart.data.labels.splice(0, 1);
      myTempChart.data.datasets.forEach((dataset) => {
        dataset.data.shift();
      });
    }
    //função que adiciona dados de humidade
    function humAddData(label, data) {
      myHumChart.data.labels.push(label);
      myHumChart.data.datasets.forEach((dataset) => {
        dataset.data.push(data);
      });
      myHumChart.update();
    }
  //função que remove a primeira leitura quando limite é atingido
    function humRemoveFirstData() {
      myHumChart.data.labels.splice(0, 1);
      myHumChart.data.datasets.forEach((dataset) => {
        dataset.data.shift();
      });
    }
  
    const MAX_DATA_COUNT = 10;//definição do limite de dados no gráfico, pode ser alterado.
    
    //conexão ao servidor socket
    var socket = io.connect();

    //Handler do evento de update das leituras de temperatura disparados no backend
    socket.on("updateTempSensorData", function (msg) {
      console.log("Received sensorData :: " + msg.date + " :: " + msg.value);

      // Checagem se o limite foi atingido
      if (myTempChart.data.labels.length > MAX_DATA_COUNT) {
        tempRemoveFirstData();
      }
      tempAddData(msg.date, msg.value);
    });

    //Handler do evento de update das leituras de humidade disparados no backend
    socket.on("updateHumSensorData", function (msg) {
      console.log("Received sensorData :: " + msg.date + " :: " + msg.value);
  
      // Checagem de limite atingido
      if (myHumChart.data.labels.length > MAX_DATA_COUNT) {
        humRemoveFirstData();
      }
      humAddData(msg.date, msg.value);
    });

    //função executada quando há alteração no input de calendário
    //dispara o evento Filtered Data no socket e aciona o handler no backend
    function filterDataOnDate(){
      var x = document.getElementById("Sdate")
      socket.emit('FilterDate', x.value)
      console.log("Filter Request :: " + x.value);
    }$("#Sdate").on("change", filterDataOnDate);


    //Handler do evento Filtered Data disparado no backend
    //Recebe os dados da data filtrada, limpa o gráfico e plota o resultado da query
    socket.on("Filtered Data", function (msg) {
      console.log("Received Filtered msg :: "+msg)
      restartCanva();
      msg.forEach(function(item) {
        tempAddData(item.currentdate, item.temperature)
        humAddData(item.currentdate, item.humidity)
    });   
    });

    //Handler do evento No Data Returned disparado do backend
    //Executa a limpeza do gráfico e dispara o alerta.
    socket.on('No Data Returned' , function(data){
      // your action on user disconnect
      document.getElementById("Sdate").value = "";
      alert("No data for " + data)
      console.log("No data for "+ data);
    });
    
    //função executada quando o botão Real Time é acionado
    //dispara o evento RunItBack no socket e aciona o handler no backend
    function restoreRealTime(){
      restartCanva();
      document.getElementById("Sdate").value = "";
      var x = document.getElementById("rtUpdate")
      socket.emit('RunItBack')
    }$("#rtUpdate").on("click", restoreRealTime);

    //Handler de desconexão do socket
    socket.on('disconnect' , function(){
      socket.broadcast.to(socket.chatroom).emit('user disconnect');
      console.log("client has disconnected:"+socket.id);
    });

    //função de limpeza do gráfico
    function restartCanva(){
      Tctx.clearRect(0, 0, myHumChart.width, myHumChart.height);
      Tctx.beginPath(); 
      Tctx.save();
      
      ctx.clearRect(0, 0, myTempChart.width, myTempChart.height);
      ctx.beginPath();
      ctx.save();
      for (let i = 0; i < 41; i++){
        humRemoveFirstData();
        tempRemoveFirstData();
      };
    };
  });