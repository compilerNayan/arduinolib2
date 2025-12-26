#ifndef HTTP_REQUEST_DISPATCHER_H
#define HTTP_REQUEST_DISPATCHER_H

#include <unordered_map>

#include "IHttpRequestDispatcher.h"

COMPONENT
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
        CStdString url = request->GetHttpUrl();
        CStdString payload = request->GetHttpPayload();
        switch (request->GetHttpMethod()) {
            case HttpMethod::Get:
                return getMappings[url](payload);
            case HttpMethod::Post:
                return postMappings[url](payload);
            case HttpMethod::Put:
                return putMappings[url](payload);
            case HttpMethod::Patch:
                return patchMappings[url](payload);
            case HttpMethod::Delete:
                return deleteMappings[url](payload);
        }
        return StdString();
    }

    Private Void InitializeMappings() {

    }

};

#endif // HTTP_REQUEST_DISPATCHER_H