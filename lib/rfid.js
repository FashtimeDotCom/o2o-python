var edge = require('./edge'), path = require('path');
var params = {
	host: 'COM3',
	port: '12345'
};
var rfid = edge.func(function() {/*

    #r "JW.UHF.dll"

    using System;
	using System.Collections.Generic;
	using System.ComponentModel;
	using System.Threading;
	using System.Threading.Tasks;
	using JW.UHF;
    using Util;

    class Startup
    {

    	private object lockObj = new object();//线程同步锁
        private DateTime startTime;//启动时间 
        private Queue<Tag> inventoryTagQueue = new Queue<Tag>();//盘点到Tag队列列表
        Dictionary<string, object> tagList = new Dictionary<string, object>();//Tag列表
        UInt64 actual_read_count = 0;//实际读取数量
        private bool stopInventoryFlag = false;//是否停止盘点标志

        private delegate void UHFOperDelegate();//UHF操作跨线程委托类
        private JWReader jwReader = null;

        /// <summary>
        /// 入口函数
        /// </summary>
        public async Task<object> Invoke(dynamic input){
            #region 连接模块
            Result result = Result.OK;
            jwReader = new JWReader(input.host);
            result = jwReader.RFID_Open();//连接UHF模块

            if (result != Result.OK)
            {
                return "不能打开读写器";
            }
            #endregion

            #region 配置模块
            RfidSetting rs = new RfidSetting();
            rs.AntennaPort_List = new List<AntennaPort>();
            AntennaPort ap = new AntennaPort();
            ap.AntennaIndex = 0;//天线1
            ap.Power = 27;//功率设为27
            rs.AntennaPort_List.Add(ap);

            rs.GPIO_Config = null;
            rs.Inventory_Time = 5000;

            rs.Region_List = RegionList.CCC;

            rs.RSSI_Filter = new RSSIFilter();
            rs.RSSI_Filter.Enable = true;
            rs.RSSI_Filter.RSSIValue = (float)-70;

            rs.Speed_Mode = SpeedMode.SPEED_FASTEST;


            rs.Tag_Group = new TagGroup();
            rs.Tag_Group.SessionTarget = SessionTarget.A;
            rs.Tag_Group.SearchMode = SearchMode.DUAL_TARGET;
            rs.Tag_Group.Session = Session.S0;

            result = jwReader.RFID_Set_Config(rs);
            if (result != Result.OK)
            {
                return "读写器设置失败";
            }
            #endregion
			
			await Task.Run(async() => {
				#region 启动盘点
	           	startInventory();
	           	#endregion
			});

			return null;
        }


        /// <summary>
        /// 关闭读写器连接
        /// </summary>
        private void closeConnect(){

            jwReader.RFID_Stop_Inventory();//停止当前UHF操作

            jwReader.RFID_Close();//关闭模块连接
        }


        /// <summary>
        /// 启动盘点
        /// </summary>
        private void startInventory(){
            clearInventoryData();//清空盘点数据

            stopInventoryFlag = false;

            Thread inventoryThread = new Thread(inventory);//盘点线程
            inventoryThread.Start();

            Thread updateThread = new Thread(updateList);//更新列表线程
            updateThread.Start();
        }


        /// <summary>
        /// 清空盘点数据
        /// </summary>
        private void clearInventoryData(){
            inventoryTagQueue.Clear();
            tagList.Clear();
            actual_read_count = 0;
        }


        /// <summary>
        /// 数据上报
        /// </summary>
        /// <param name="sender"></param>
        /// <param name="args"></param>
        private void TagsReport(object sender, TagsEventArgs args){
            Tag tag = args.tag;
            inventoryTagQueue.Enqueue(tag);//回调函数事情越少越好。
        }


        /// <summary>
        /// 盘点线程
        /// </summary>
        void inventory(){
            jwReader.TagsReported += TagsReport;
            //盘点
            jwReader.RFID_Start_Inventory();
        }


        /// <summary>
        /// 更新列表线程
        /// </summary>
        private void updateList(){
            while (!stopInventoryFlag)//未停止
            {
                updateInventoryGridList();
                Thread.Sleep(100);
            }
            
            DateTime dt = DateTime.Now;
            while (true)
            {
                updateInventoryGridList();
                //500毫秒内确定没有包了 防止线程提前结束 有些盘点包还没处理完 可保证该线程最后结束。
                if (inventoryTagQueue.Count == 0 && Util.DateDiffMillSecond(DateTime.Now, dt) > 500)
                    break;
            }
        }


        /// <summary>
        /// 更新列表
        /// </summary>
        private void updateInventoryGridList(){
            UHFOperDelegate updateList = delegate()
            {
                while (inventoryTagQueue.Count > 0)
                {
                    Tag packet = inventoryTagQueue.Dequeue();
                    String epc = packet.EPC;
                    if (tagList.ContainsKey(epc)){
                        
                    }else{
                        #region 新增列表
                        string item = packet.EPC;

                        this.tagList.Add(packet.EPC, item);
                        this.actual_read_count++;
                        #endregion
                    }

                }//while循环
            };

            this.Invoke(updateList);
        }


        /// <summary>
        /// 停止盘点
        /// </summary>
        private void stopBtn_Click(){
            jwReader.RFID_Stop_Inventory();//停止当前UHF操作
            jwReader.TagsReported -= TagsReport;
            stopInventoryFlag = true;
        }
    }
*/});

rfid(params, function(err, result){
	if(err) throw err;
	console.log(result);
});