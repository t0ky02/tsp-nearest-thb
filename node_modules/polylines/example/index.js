class PolyLine {
  constructor(el) {
    this.canvas = document.createElement("canvas");
    if(!this.canvas || !this.canvas.getContext) return null;
    this.el = el;
    this.el.appendChild(this.canvas);
    this.canvas.innerHTML = '你的浏览器不支持HTML5 canvas';
    this.width = el.clientWidth;
    this.height = el.clientHeight;
    this.isAnimate =true;//动画标志
    this.dotArr = [];//画布上的点坐标数组
    this.dotIndex = '';//鼠标所在绘制竖线的坐标序号+1
    this.ctx = this.canvas.getContext("2d");//canvas上下文

    /*这里是对高清屏幕的处理，
      方法：先将canvas的width 和height设置成本来的ratio倍
      然后将style.height 和 style.width设置成本来的宽高
      这样相当于把两倍的东西缩放到原来的 ratio倍，这样在高清屏幕上 一个像素的位置就可以有ratio个像素的值
      这样需要注意的是所有的宽高间距，文字大小等都得设置成原来的ratio倍才可以。
    */
    let backingStore = this.ctx.backingStorePixelRatio || this.ctx.webkitBackingStorePixelRatio || this.ctx.mozBackingStorePixelRatio || this.ctx.msBackingStorePixelRatio || this.ctx.oBackingStorePixelRatio || this.ctx.backingStorePixelRatio || 1;
    this.ratio = (window.devicePixelRatio || 1) / backingStore;
    this.canvas.width = this.width*this.ratio ;
    this.canvas.height = this.height *this.ratio ;
    this.canvas.style.height = this.canvas.height/ this.ratio + "px";
    this.canvas.style.width = this.canvas.width/ this.ratio + "px";

      // ratio = 2
      // ctx.scale(2, 2)
  }
  /**
   data 数据[[x1,y1],[x2,y2],[x3,y3]]
   clearY, 清盘线y值
   totalYNomber 纵坐标y坐标个数
   animation:初始的绘制动画参数（y值变化）
   {
    ctr:每次绘制的量化份数,默认5
    numctr: 总量化份数,默认100
    speed:每次绘制的时间间隔(ms),默认30ms
   }
 **/
  setOption({data, clearY, totalYNomber=10, animation={}}){
    this.cMargin = 5*this.ratio;//坐标轴区域距画布左、上间隔
    this.cSpace = 45*this.ratio;//坐标轴区域距画布左、下间隔
    this.cHeight = this.canvas.height - this.cMargin - this.cSpace ;//坐标系高度
    this.cWidth = this.canvas.width - this.cMargin - this.cSpace - 30;//坐标宽度（坐标轴距画布右侧留出30的区域，防止标注超出画布范围）
    this.originX = this.cMargin + this.cSpace;//坐标原点在canvas画布上的x坐标
    this.originY = this.cMargin + this.cHeight;//坐标原点在canvas画布上的y坐标
    this.data = data;
    this.tobalDots = data.length;//数据坐标点个数
    this.dotSpace = this.cWidth/(this.tobalDots - 1);//横坐标间距
    this.maxValue = data.reduce((prev, curr)=>{
      return prev[1] > curr[1] ? prev: curr;
   })[1] + 50;//最大纵坐标值（最大纵坐标值与最大数据值有50的余量）
   this.clearPlot = this.originY -  (clearY / this.maxValue) * this.cHeight;//清盘线Y坐标
   this.totalYNomber = totalYNomber;
   // 运动相关(初始的绘制动画)
   this.animation = {
    ctr: animation.ctr || 5,
    numctr: animation.numctr || 100,
    speed: animation.speed || 30
   } ;
   this.ctx.translate(0.5*this.ratio, 0.5*this.ratio);  // 当只绘制1像素的线的时候，坐标点需要偏移，这样才能画出1像素实线

   this.drawLineLabelMarkers(); // 绘制图表轴、标签和标记
   this.drawLineAnimate(); //
  }
  
  // 绘制图表轴、标签和标记
  drawLineLabelMarkers(){
    let {ratio, originX, originY, cMargin, cWidth, ctx} = this;
    ctx.font = 12*ratio + "px Arial";
    ctx.lineWidth = 1*ratio;
    ctx.fillStyle = "#566a80";
    ctx.strokeStyle = "#566a80";
    // y轴线
    this.drawLine(originX, originY, originX, cMargin);
    // x轴线
    this.drawLine(originX, originY, originX+cWidth, originY);

    // 绘制标记
    this.drawMarkers();
    ctx.lineWidth = 1*ratio;
  }

  // 画线的方法
  drawLine(x, y, X, Y){
    let ctx = this.ctx;
    ctx.beginPath();
    ctx.moveTo(x, y);
    ctx.lineTo(X, Y);
    ctx.stroke();
    ctx.closePath();
  }
  // 绘制标记
  drawMarkers(){
    let {data, ctx, dotSpace, maxValue, totalYNomber, originX, originY, ratio, cWidth, cHeight, cMargin, cSpace} = this;
    ctx.strokeStyle = "#E0E0E0";
    // 绘制 y 轴标记 及中间横线
    let oneVal = parseInt(maxValue / totalYNomber);//y轴基本刻度
    ctx.textAlign = "right";
    Array.from({length: totalYNomber+1}, (v, k) => k).forEach((v,i) => {
      let markerVal =  i*oneVal;
      let xMarker = originX-5*ratio;
      let yMarker = parseInt( cHeight*(1 - markerVal / maxValue) ) + cMargin;
      ctx.fillText(markerVal, xMarker, yMarker+10*ratio); // 文字
      if(i>0){
        ctx.lineWidth = 1*ratio;
        this.drawLine(originX+2*ratio, yMarker, originX+cWidth, yMarker);//中间横线
      }
    });
    // for(let i=0; i<=totalYNomber; i++){
    //     let markerVal =  i*oneVal;
    //     let xMarker = originX-5*ratio;
    //     let yMarker = parseInt( cHeight*(1-markerVal/maxValue) ) + cMargin;

    //     ctx.fillText(markerVal, xMarker, yMarker+5*ratio, cSpace); // 文字
    //     if(i>0){
    //         ctx.lineWidth = 1*ratio;
    //         this.drawLine(originX+2*ratio, yMarker, originX+cWidth, yMarker);//中间横线
    //     }
    // }

    // 绘制 x 轴标记 及中间竖线
    ctx.textAlign = "center";
    let num = Math.ceil(75*ratio / dotSpace);//x轴坐标显示间隔最少75px
    data.forEach((v,i) => {
      if(i%num!==parseInt(num / 2)) return;
        let markerVal = v[0];
        let xMarker = originX+i*dotSpace;
        let yMarker = originY+20*ratio;
        ctx.fillText(markerVal, xMarker, yMarker);
        // if(i>0){
        //     drawLine(xMarker, originY-2, xMarker, cMargin);
        // }
    });
    // for(let i=0; i<tobalDots; i++){
    //     if(i%num!==parseInt(num / 2)) continue;
    //     let markerVal = data[i][0];
    //     let xMarker = originX+i*dotSpace;
    //     let yMarker = originY+20*ratio;
    //     ctx.fillText(markerVal, xMarker, yMarker); // 文字
    //     // if(i>0){
    //     //     drawLine(xMarker, originY-2, xMarker, cMargin);
    //     // }
    // }

    // 绘制标题 y
    // ctx.save();
    // ctx.rotate(-Math.PI/2);
    // ctx.fillText("访问量", -canvas.height/2, originX-50*ratio);
    // ctx.restore();//获取save时的设置
    // 绘制标题 x
    ctx.fillText("月份", originX+cWidth/2, originY+cSpace/2+20*ratio);
  };
  //绘制折线图
  drawLineAnimate(){
    let {data, ctx, dotSpace, dotArr, dotIndex, clearPlot, tobalDots, maxValue, originX, originY, ratio, cWidth, cHeight, cMargin} = this;
    ctx.strokeStyle = "orange";  //"#49FE79";
    ctx.lineWidth = 2*ratio;
    //连线
    ctx.beginPath();
    data.forEach((v,i)=>{
      let dotVal = v[1];
      let barH = parseInt( cHeight * dotVal / maxValue * this.animation.ctr / this.animation.numctr );//y轴一次绘制ctr/numctr(设置动画初始百分比率)al/ max
      let y = originY - barH;
      let x = originX + dotSpace*i;
      if(i==0){
          ctx.moveTo( x, y );
      }else{
          ctx.lineTo( x, y );
      }
    })
    // for(let i=0; i<tobalDots; i++){
    //   let dotVal = data[i][1];
    //   let barH = parseInt( cHeight * dotVal / maxValue * this.animation.ctr / this.animation.numctr );//y轴一次绘制ctr/numctr(设置动画初始百分比率)al/ max
    //   let y = originY - barH;
    //   let x = originX + dotSpace*i;
    //   if(i==0){
    //       ctx.moveTo( x, y );
    //   }else{
    //       ctx.lineTo( x, y );
    //   }
    // }
    ctx.stroke();


    //背景
    ctx.lineTo( originX+dotSpace*(tobalDots-1), originY);
    ctx.lineTo( originX, originY);
    //背景渐变色
    let gradient = ctx.createLinearGradient(originX, originY, originX, cMargin);
    gradient.addColorStop(0, 'rgba(255,165,0,0.01)');
    gradient.addColorStop(1, 'rgba(255,165,0,0.6)');
    ctx.fillStyle = gradient;
    ctx.fill();
    ctx.closePath();
    ctx.fillStyle = "#566a80";

    // 绘制清盘线
    this.drawDottedX(originX, clearPlot, originX+cWidth, clearPlot)
    ctx.strokeStyle = "#EEEEEE";
    ctx.strokeRect(originX+cWidth-48*ratio, clearPlot, 48*ratio, 20*ratio);
    ctx.fillStyle = "#EEEEEE";
    ctx.fillRect(originX+cWidth-48*ratio, clearPlot+1, 48*ratio, 20*ratio);
    ctx.fillStyle = "#999999";
    ctx.font = 12*ratio + "px Arial";
    ctx.fillText('清盘线', originX+cWidth-24*ratio, clearPlot+15*ratio); // 文字


    //绘制点
    if(dotIndex) {
        this.drawDottedY(dotArr[dotIndex-1][0], originY, dotArr[dotIndex-1][0], cMargin)
        this.drawArc( dotArr[dotIndex-1][0], dotArr[dotIndex-1][1] );  //绘制点
        ctx.fillStyle = "orange";
        ctx.fillText(data[dotIndex-1][1], dotArr[dotIndex-1][0]+10, dotArr[dotIndex-1][1]-2); // 文字
    }
    if(!this.isAnimate) return
    if(this.animation.ctr<this.animation.numctr){
      this.animation.ctr += 6;
      setTimeout(()=>{
        ctx.clearRect(0,0,this.canvas.width, this.canvas.height);
        this.drawLineLabelMarkers();
        this.drawLineAnimate();
      }, this.animation.speed);
    }
    if(this.animation.ctr>=this.animation.numctr){
      this.isAnimate = false;
      this.animation.ctr = this.animation.numctr;
      data.forEach((v,i)=>{
        let dotVal = v[1],
            barH = parseInt( cHeight * dotVal / maxValue),
            y = originY - barH,
            x = originX + dotSpace*i;
        this.dotArr.push([x, y]);
          // drawArc( x, y );  //绘制点
          // ctx.fillStyle = "orange";
          // ctx.fillText(parseInt(dotVal*ctr/numctr), x+20, y-8); // 文字
        })
        // for(let i=0; i<tobalDots; i++){
        //     let dotVal = dataArr[i][1];
        //     let barH = parseInt( cHeight*dotVal/maxValue);
        //     let y = originY - barH;
        //     let x = originX + dotSpace*i;
        //     dotArr.push([x, y])
        //     // drawArc( x, y );  //绘制点
        //     // ctx.fillStyle = "orange";
        //     // ctx.fillText(parseInt(dotVal*ctr/numctr), x+20, y-8); // 文字
        // }
        this.canvas.onmousemove=(e)=>{
            if(e.offsetX*ratio <= originX || e.offsetY >= originY || e.offsetX*ratio >= originX+cWidth || e.offsetY <= cMargin) return;
            let index = Math.round((e.offsetX*ratio - originX) / dotSpace) + 1
            if(index!== dotIndex) {
                this.dotIndex = dotIndex = index;
                ctx.clearRect(0,0,this.canvas.width, this.canvas.height);
                this.drawLineLabelMarkers();
                this.drawLineAnimate();

            }
        }
    }
  }

  //绘制圆点
  drawArc( x, y ){
    let ctx = this.ctx;
    ctx.fillStyle = "orange";
    ctx.beginPath();
    ctx.arc( x, y, 5*this.ratio, 0, Math.PI*2*this.ratio );
    ctx.fill();
    ctx.closePath();

    ctx.fillStyle = "#FFFFFF";
    ctx.beginPath();
    ctx.arc( x, y, 3*this.ratio, 0, Math.PI*2*this.ratio );
    ctx.fill();
    ctx.closePath();
  }

  // 绘制纵向虚线
  drawDottedY( x, y, X, Y ){
    let ctx = this.ctx;
    ctx.lineWidth = 1 *this.ratio;
    ctx.strokeStyle = "orange";
    let length = this.cHeight / (7*this.ratio);
    for(let i=0; i<length; i++){
      if(i%2 === 1 || x=== this.originX) continue;
      ctx.beginPath();
      ctx.moveTo(x, y + (Y-y)*i / length);
      ctx.lineTo(X, y + (Y-y)*(i+1) / length);
      ctx.stroke();
      ctx.closePath();
    }
  }
  // 绘制横向虚线
  drawDottedX( x, y, X, Y ){
    let ctx = this.ctx;
    ctx.strokeStyle = "green";
    ctx.lineWidth = 1 *this.ratio;
    let length = this.cWidth / (2*this.ratio);
    for(let i=0; i<length; i++){
      if(i%2 === 1) continue;
      ctx.beginPath();
      ctx.moveTo(x + (X-x)*i / length, y);
      ctx.lineTo(x + (X-x)*(i+1) / length, Y);
      ctx.stroke();
      ctx.closePath();
    }
  }

}
window.polyLine = {
  init(element){
    return new PolyLine(element);
  }
}
