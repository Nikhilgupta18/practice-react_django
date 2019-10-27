import React, { Component } from 'react';
import 'whatwg-fetch'
import cookie from 'react-cookies'
import { Link, useParams, Route } from 'react-router-dom'
import PostInline from "./posts/PostInline";


class AllServices extends Component {

    constructor(props) {
        super(props);
        this.loadServices =this.loadServices.bind(this)
        this.state = {
            services: [],
        }
    }



    loadServices() {
        let endpoint = '/api/service/all_services/'
        let thisComp = this;
        let lookupOptions = {
            method: "GET",
            headers: {
                'Content-Type': 'application/json'
            }
        };
        const csrfToken = cookie.load('csrftoken')
        if (csrfToken !== undefined) {
            lookupOptions['credentials'] = 'include'
            lookupOptions['headers']['X-CSRFToken'] = csrfToken
        }

        fetch(endpoint, lookupOptions)
            .then(function (response) {
                return response.json()
            }).then(function(responseData){

            thisComp.setState({
                services: responseData.services,
            })
        }).catch(function (error) {
            console.log("error", error)
        })
    }

componentDidMount(){

      this.loadServices();
  }
  render() {
      // this.loadServices();


      const services = this.state.services;

    return (
      <div>
          <section id="services" style={{marginTop: 100}}>
              <div className="container">

                  <header className="section-header wow fadeInUp">
                      <h3>Services</h3>
                      <p>Having Worked With Students From Over 22 Countries And Interviewed Multiple Professors, I Know
                          Exactly What The Admissions Committee Likes to See in Their Applicants. Now You Can Learn My
                          Secret To Cracking The Admissions Process And Implement it in Your Application.</p>

                  </header>


                  <div className="row" style={{width: 105 + '%'}}>
            {/*let {service_name} = this.props;*/}
          {services.length > 0 ? services.map((service, index)=>{
              return (


                  <div className="col-lg-4 col-md-6 ">
                      <Link maintainScrollPosition={false} to={{
                   pathname:`/service/premium/${service.link}`,
                   state: {fromDashboard: false}
               }}>
                      <div
                              className=" box wow bounceInUp pinned-item-list-item p-3 mb-3 border border-gray-dark rounded-1 public source"
                              data-wow-duration="1.4s">
                              <div className="icon" ><i className={service.faicon}></i> </div>
                              <h4 className="title" style={{color: `black`}}>{service.heading}</h4>
                              <p className="description" style={{color: `#666666`}}>{service.intro}</p>
                          </div>
                      </Link>

                  </div>
              )
          }) : <p>No Services Found</p>}

          </div>

      </div>
    </section>
      </div>
    );
  }
}

export default AllServices;


