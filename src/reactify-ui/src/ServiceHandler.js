import React, { Component } from 'react';
import 'whatwg-fetch'
import cookie from 'react-cookies'
import {withRouter} from 'react-router-dom';
// import { Link, useParams } from 'react-router-dom'
// import PostInline from "./posts/PostInline";


class ServiceHandler extends Component {

    constructor(props) {
        super(props);
        this.servicehandler = this.servicehandler.bind(this)
        this.state = {
            service: [],
            user:'',

            // consult_list: [],
            // testimonials: 0,
            // heading: '',
            // service_name: '',
            // intro: '',

        }
    }



    servicehandler() {

        let thisComp = this;
        let p = this.props.location.pathname;


        let s = p.split('/');
        let last = s[s.length-1];


        let u = window.django.user.username;
        let data = {'link': last,
                    'user':u};
        let endpoint = `/api/service/${last}/`;

        let lookupOptions = {
            method: "POST",
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        };
        // let {service_name} = useParams();
        // console.log({service_name});
        const csrfToken = cookie.load('csrftoken')
        if (csrfToken !== undefined) {
            lookupOptions['credentials'] = 'include'
            lookupOptions['headers']['X-CSRFToken'] = csrfToken
        }

        fetch(endpoint, lookupOptions)
            .then(function (response) {
                return response.json()
            }).then(function(responseData){
            console.log(responseData);
            thisComp.setState({
                service: responseData.service,
                user: responseData.user,
                // testimonials: responseData.testimonials,
                // consult_list: responseData.consult_list,


            })

        }).catch(function (error) {
            console.log("error", error)
        })
    }


componentDidMount(){

        this.servicehandler();
  }
  render() {

      const {service} = this.state;
      const {user} = this.state;
      let u = window.django.user.username;
      console.log(u);

    return (
      <div>
          <div className="banner" style={{marginTop: `70px`}}>

              <h1 style={{color: `white`, marginTop: `90px`,textAlign:`center`}} className="frmt">

              </h1>
              <h2 style={{color: `white` , marginTop: `70px`, textAlign:`center`,fontSize: `25px`,padding:`0 5% 0 5%`}} className="frmt1">
                  {service.intro}
              </h2>

          </div>
          <section id="features" className="section" style={{marginTop: `80px`}}>
          <div className="container">
              <div className="row">
                  <div className="col-md-7">
                      <div className="section-header">
                        <h2 className="section-title">About service</h2>

                        <p className="section-subtitle" style={{textAlign: `justify`, justifyContent: `flex-end`}}>{service.details}</p>

                      </div>
                      {user === true ?
                      <div className="section-header">
                          <a href="/service/publish-testimonial/{service.heading}/"><button className="rzp-button1 btn btn-lg btn-success">Write a Testimonial</button></a>
                          you are logged in.
                      </div> :
                      <div>
                            <div class="section-header">
                                  <a href="/service/publish-testimonial/{service.heading}/"><button className="rzp-button1 btn btn-lg btn-success" disabled>Write a Testimonial</button></a>
                              </div>
                                  <p className="text-danger">You cannot publish testimonials because you have not purchased any services yet.</p>
                      </div>}


                  <div className="col-md-4">
                      <div className="item-boxes services-item wow fadeInDown" data-wow-delay="0.2s">
                                          <div className="ribbon"><span>Launch Offer</span></div>

                                                    <h4>Details</h4>
                          {service.spl_details}


    {/*{service.spl_details}*/}

      </div>
                  </div>
                  </div>
              </div>
          </div>
          </section>
      </div>
    );
  }
}


export default ServiceHandler;


