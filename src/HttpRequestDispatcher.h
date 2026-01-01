#ifndef HTTP_REQUEST_DISPATCHER_H
#define HTTP_REQUEST_DISPATCHER_H

#include <unordered_map>
#include <NayanSerializer.h>

#include "IHttpRequestDispatcher.h"

//@Component
class HttpRequestDispatcher : public IHttpRequestDispatcher {

    Private std::unordered_map<StdString, std::function<StdString(CStdString)>> getMappings;
    Private std::unordered_map<StdString, std::function<StdString(CStdString)>> postMappings;
    Private std::unordered_map<StdString, std::function<StdString(CStdString)>> putMappings;
    Private std::unordered_map<StdString, std::function<StdString(CStdString)>> patchMappings;
    Private std::unordered_map<StdString, std::function<StdString(CStdString)>> deleteMappings;

    Public HttpRequestDispatcher() {
        InitializeMappings();
    }

    Public ~HttpRequestDispatcher() = default;

    Public StdString DispatchRequest(IHttpRequestPtr request) override {
        CStdString url = request->GetPath();
        CStdString payload = request->GetBody();
        switch (request->GetMethod()) {
            case HttpMethod::GET:
                return getMappings[url](payload);
            case HttpMethod::POST:
                return postMappings[url](payload);
            case HttpMethod::PUT:
                return putMappings[url](payload);
            case HttpMethod::PATCH:
                return patchMappings[url](payload);
            case HttpMethod::DELETE:
                return deleteMappings[url](payload);
        } 
        return StdString();
    }

    Private Void InitializeMappings() {

    }

};

#endif // HTTP_REQUEST_DISPATCHER_H