import React, { Component } from 'react';
import Axios from 'axios';
import 'bulma/css/bulma.css';
import './App.css';
import { Container, Button,TextArea ,Image} from 'bloomer'
import Logo from './logo.jpg'

const buttonStyle={
  display:"flex",
  justifyContent : 'center',
  marginTop : '20px'
}

const buttonStyle1={
  display:"flex",
  justifyContent : 'center',
}

const padding={
  marginTop : '20px',
  paddingTop: "20px"
}

const titlestyle={
  marginBottom: "20px",
}

const textstyle={
  marginBottom:"20px",
}

const imgcountstyle={
  marginRight:"5px"
}
const vidcountstyle={
  marginRight:"5px"
}
const linkcountstyle={
  marginRight:"5px"
}

class App extends Component {
  constructor(props) {
    super(props);
    this.state = {text:'',title:'',img_count:0,vid_count:0,link_count:0,showMessage:0,stru:0,trend:0}
    this.changeText = this.changeText.bind(this)
    this.changeTitle = this.changeTitle.bind(this)
    this.changeImgcount = this.changeImgcount.bind(this)
    this.changeVidcount = this.changeVidcount.bind(this)
    this.changeLinkcount = this.changeLinkcount.bind(this)
    this.submitText = this.submitText.bind(this)
  }
  changeText(e){
    this.setState({text:e.target.value})
  }
  changeTitle(e){
    this.setState({title:e.target.value})
  }
  changeImgcount(e){
    this.setState({img_count:e.target.value})
  }
  changeVidcount(e){
    this.setState({vid_count:e.target.value})
  }
  changeLinkcount(e){
    this.setState({text:'',title:'',img_count:0,vid_count:0,link_count:0})
  }
  submitText(){
    this.setState({showMessage:1})
    var self = this;
    Axios.post('http://0.0.0.0:5000/', {
      title: this.state.title,
      text: this.state.text,
      image_count : this.state.img_count,
      video_count : this.state.vid_count,
      link_count : this.state.link_count,
      location : "23424848"
     },).then(function (response) {
      if(response){
        self.setState({showMessage:2,stru:response.data["structural_a"],trend:response.data["trend"]})
      }
      console.log(response.data["structural_a"])
    }).catch(function (error) {
      console.log(error);
    });

    this.setState({text:'',title:'',img_count:0,vid_count:0,link_count:0})
  }
  
  render() {
    return (
       <Container>

        <div style={buttonStyle1}><Image src={Logo}/></div>
        <div style={buttonStyle1}><h2 style={{fontSize:"30px"}}>Generate Popularity of Articles</h2></div>
        <form style={padding}>
         <TextArea style={titlestyle} isColor='info' placeholder="Enter Title" fullWidth={true} multiline={true} rows='1' value={this.state.title} onChange={this.changeTitle}/>
          <TextArea style={textstyle} placeholder="Enter Text" fullWidth={true} multiline={true} rows='10' value={this.state.text} onChange={this.changeText}/>
          <div style={buttonStyle}>
          <input style={imgcountstyle} class="input" type="number" placeholder="Image Count" onChange></input>
          <input style={vidcountstyle} class="input" type="number" placeholder="Video Count" onChange></input>
          <input style={linkcountstyle} class="input" type="number" placeholder="Link Count" onChange></input>
          </div>
          <div style={buttonStyle}>
          <Button  isColor='info' onClick={this.submitText}>Submit</Button>
          </div>
        </form>
{this.state.showMessage ==0 ? "" : this.state.showMessage==1?<div style={buttonStyle}><span>Processing Your Request... In the meantime Grab a Coffee</span></div>:<div></div>}
       </Container>
    );
  }
}

export default App;
