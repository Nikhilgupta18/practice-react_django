import React, { Component } from 'react';
import { BrowserRouter, Route, Redirect, Switch} from 'react-router-dom'
import logo from './logo.svg';
import './App.css';

import Posts from './posts/Posts';
import PostDetail from './posts/PostDetail';
import PostCreate from './posts/PostCreate'
import AllServices from './AllServices';
import ServiceHandler from "./ServiceHandler";
class App extends Component {
  render() {
              console.log('avc');

    return (
      <BrowserRouter>
          <Switch>
            {/*<Route exact path='/posts/create' component={PostCreate}/>*/}
            <Route exact path='/service/' component={AllServices}/>
            <Route exact path='/service/premium/:service_name/' component={ServiceHandler}/>

            {/*<Route exact path='/posts' component={Posts}/>*/}
            {/*<Route exact path='/posts/:slug' component={PostDetail}/>*/}
            <Route component={AllServices}/>
          </Switch>
      </BrowserRouter>
    );
  }
}

export default App;
