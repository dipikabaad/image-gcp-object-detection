import React, { Component } from 'react';
import Navbar from 'react-bootstrap/Navbar';
import Nav from 'react-bootstrap/Nav';
import Form from 'react-bootstrap/Form';
import FormControl from 'react-bootstrap/FormControl';
import DropdownButton from 'react-bootstrap/DropdownButton';
import Dropdown from 'react-bootstrap/Dropdown';
import Button from 'react-bootstrap/Button';
import './App.css';
import Gallery from 'react-grid-gallery';


class App extends Component {
  constructor(props){
    super(props);
    this.state = {
      model_results_data: [],
      filtered_model_results: [],
      images: [],
      images_loaded: false,
      search_text: "",
    }
    this.location_filter = this.location_filter.bind(this);

  }

  load_images = (image_paths, output_file_path) => {

  }

  componentDidMount(){
    let images_to_be_rendered = []
    let output_file_path = ""
    fetch('http://127.0.0.1:5000/get_data').then(res => res.json())
    .then((data) => {
      data['results'].map( function(data1, index1) {
        output_file_path = data1['output_file_path']
        images_to_be_rendered.push({
          src: 'https://storage.cloud.google.com/netlight-all-images/' + output_file_path,
          thumbnail: 'https://storage.cloud.google.com/netlight-all-images/' + output_file_path,
          thumbnailWidth: 320,
          thumbnailHeight: 320,

          caption: data1['detected_objects']
        })
      })

        this.setState({ model_results_data : data['results'], filtered_model_results: data['results'],
        images_loaded: true, images: images_to_be_rendered})
    })
  }

  componentDidUpdate(){

  }
  location_filter(e){
    // e is the choice from the dropdown
    let filtered_data = []
    let images_to_be_rendered = []
    let output_file_path = ""


    if (e !==  "All"){
      filtered_data = this.state.model_results_data.filter((x) => { return (x.location===e)})
    }
    else {
      filtered_data = this.state.model_results_data
    }
    console.log(e)
    filtered_data.map(function(data, index){
      output_file_path = data['output_file_path']
      images_to_be_rendered.push({
        src: 'https://storage.cloud.google.com/netlight-all-images/' + output_file_path,
        thumbnail: 'https://storage.cloud.google.com/netlight-all-images/' + output_file_path,
        thumbnailWidth: 320,
        thumbnailHeight: 320,
        caption: data['detected_objects']
      })
      return null;
    })

      this.setState({ filtered_model_results: filtered_data, images_loaded: true, images: images_to_be_rendered})

  }
  setSearch = (e) => {
    this.setState({ search_text: e.target.value})
  }

  handleSearch = (e) => {
    let model_data = this.state.filtered_model_results
    let output_file_path = ""
    let images_to_be_rendered = []
    // console.log(model_data)
    let filtered_data = model_data.filter((x) => { return (x['detected_objects'].includes(this.state.search_text))})
    // console.log(filtered_data)
    filtered_data.map(function(data, index){
      output_file_path = data['output_file_path']
      images_to_be_rendered.push({
        src: 'https://storage.cloud.google.com/netlight-all-images/' + output_file_path,
        thumbnail: 'https://storage.cloud.google.com/netlight-all-images/' + output_file_path,
        thumbnailWidth: 320,
        thumbnailHeight: 320,
        caption: data['detected_objects']
      })
    })
      this.setState({ images_loaded: true, images: images_to_be_rendered})

  }

  render() {
    return ( <div style={{}}>
      <Navbar bg="dark" variant="dark" style={{ width: "100%"}}>
        <Navbar.Brand href="#home">Netlight</Navbar.Brand>
        <Nav className="mr-auto">
        <DropdownButton id="dropdown-basic-button" title="Location" onSelect={this.location_filter}>
          <Dropdown.Item eventKey="All">All</Dropdown.Item>
          <Dropdown.Item eventKey="Helsinki">Helsinki</Dropdown.Item>
          <Dropdown.Item eventKey="Berlin">Berlin</Dropdown.Item>
          <Dropdown.Item eventKey="Stockholm">Stockholm</Dropdown.Item>
          <Dropdown.Item eventKey="Zurich">Zurich</Dropdown.Item>
          <Dropdown.Item eventKey="Frankfurt">Frankfurt</Dropdown.Item>
          <Dropdown.Item eventKey="Munich">Munich</Dropdown.Item>
          <Dropdown.Item eventKey="Copenhagen">Copenhagen</Dropdown.Item>
          <Dropdown.Item eventKey="Oslo">Oslo</Dropdown.Item>
        </DropdownButton>
        </Nav>
        <Form inline>
          <FormControl type="text" placeholder="Search" className="mr-sm-2"  onChange={this.setSearch}/>
          <Button variant="outline-info" type="Button" onClick={this.handleSearch}>Search</Button>
        </Form>
      </Navbar>
      <br></br>
      {/* <ImageGallery items={this.state.images} /> */}
       {/*<img src={process.env.PUBLIC_URL + '/output_images/61339690_183757715951672_6597108347406805921_n-2019-08-27-111614.jpg'} />*/}
       { this.state.images_loaded ? <div style={{width: '100%', height: '500px', float: 'left',position: "relative"}}>

       <Gallery images={this.state.images}/>
       </div> :
       <div style={{width: '100%', height: '200px', float: 'left',position: "relative", background: "blue"}}></div>
     }
    </div>
  );
  }
}

export default App;
